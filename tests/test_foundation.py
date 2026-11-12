from datetime import datetime,timedelta,timezone
import math
import sqlite3
import pytest
from sqlalchemy import select,inspect,text
from sqlalchemy.exc import IntegrityError
from database.connection import session_scope,get_engine
from database.models import *
from database.models.base import utcnow
from scripts.manage import migrate,backup,bootstrap
from modules.authentication.service import authenticate,Principal,AccessDenied,create_user,set_user_active,password_hash
from modules.assets.service import assets,create_asset,set_organisation_active
from modules.data_acquisition.service import parameters,record_measurement
from modules.monitoring.service import measurements,alerts,alert_events,evidence
from modules.monitoring.demo import seed_demo
from modules.alerts.service import record_event


def p(setup,code='top_oil'):
    return next(p for p in parameters(setup['a']) if p['code']==code)


def add(setup,value=70,asset=None,when=None):
    parameter=p(setup)
    return record_measurement(setup['a'],asset or setup['oil'],parameter['id'],value,when or utcnow(),parameter['unit'])


def test_schema_migration_repeat(setup):
    migrate()
    tables=inspect(get_engine()).get_table_names()
    assert len(Base.metadata.tables)==33
    assert len(tables)==34
    with get_engine().connect() as c:
        assert c.execute(text('PRAGMA foreign_keys')).scalar()==1
        assert c.execute(text('PRAGMA foreign_key_check')).all()==[]


def test_passwords_hashed_and_login(setup):
    principal=authenticate(' ADMIN-A@example.test ','A-long-test-password!')
    assert principal==setup['a']
    with session_scope() as s:
        assert s.get(User,principal.user_id).password_hash.startswith('$argon2id$')
    with pytest.raises(AccessDenied):authenticate('admin-a@example.test','bad')


def test_lockout_commits(setup):
    for _ in range(5):
        with pytest.raises(AccessDenied):authenticate('admin-a@example.test','wrong')
    with pytest.raises(AccessDenied):authenticate('admin-a@example.test','A-long-test-password!')
    with session_scope() as s:assert s.get(User,setup['a'].user_id).locked_until>utcnow()


def test_cross_tenant_reads_and_writes(setup):
    assert setup['asset_b'] not in {x['id'] for x in assets(setup['a'])}
    with pytest.raises(AccessDenied):measurements(setup['a'],setup['asset_b'])
    with pytest.raises(AccessDenied):add(setup,asset=setup['asset_b'])
    with pytest.raises(AccessDenied):create_asset(setup['a'],setup['station_b'],setup['kind'],'X','Wrong station',transformer={'rating_kva':100,'primary_kv':11,'secondary_kv':0.415})


def test_database_prevents_cross_tenant_links(setup):
    with pytest.raises(IntegrityError):
        with session_scope() as s:
            s.add(Asset(organisation_id=setup['org_a'],substation_id=setup['station_b'],asset_type_id=setup['kind'],code='EVIL',name='Cross tenant',status='In service',criticality='Low'));s.flush()


def test_database_prevents_same_tenant_sensor_mismatch(setup):
    parameter=p(setup)
    with session_scope() as s:
        source=DataSource(organisation_id=setup['org_a'],code='sensor-test',name='Sensor test',source_type='sensor');s.add(source)
        sensor=Sensor(organisation_id=setup['org_a'],asset_id=setup['dry'],parameter_id=parameter['id'],code='SENSOR-1',communication_status='Offline');s.add(sensor);s.flush()
        source_id=source.id;sensor_id=sensor.id
    with pytest.raises(IntegrityError):
        with session_scope() as s:
            s.add(Measurement(organisation_id=setup['org_a'],asset_id=setup['oil'],parameter_id=parameter['id'],source_id=source_id,sensor_id=sensor_id,observed_at=utcnow(),recorded_at=utcnow(),value=70,unit='°C',raw_value=70,raw_unit='°C',quality='unverified',dedupe_key='bad-sensor'));s.flush()


def test_dry_type_rejects_oil(setup):
    with pytest.raises(ValueError,match='not applicable'):add(setup,asset=setup['dry'])

@pytest.mark.parametrize('value',[math.nan,math.inf,-math.inf,True])
def test_invalid_numbers(setup,value):
    with pytest.raises(ValueError):add(setup,value)


def test_timestamps_and_duplicates(setup):
    observed=datetime(2026,1,1,12,tzinfo=timezone(timedelta(hours=3)))
    first,new=add(setup,when=observed);assert new
    second,new=add(setup,when=observed);assert first==second and not new
    with pytest.raises(ValueError,match='different value'):add(setup,value=71,when=observed)
    rows=measurements(setup['a'],setup['oil'])
    assert len(rows)==1 and rows[0]['observed_at'].hour==9
    assert rows[0]['recorded_at']>observed
    with pytest.raises(ValueError):add(setup,when=datetime(2026,1,1))


def test_viewer_cannot_write_or_impersonate(setup):
    viewer=Principal(create_user(setup['a'],'viewer@example.test','Viewer','A-long-viewer-password!','viewer'))
    assert len(assets(viewer))==2
    parameter=p(setup)
    with pytest.raises(AccessDenied):record_measurement(viewer,setup['oil'],parameter['id'],70,utcnow(),'°C')
    with pytest.raises(AccessDenied):create_user(viewer,'evil@example.test','Evil','A-long-viewer-password!','organisation_admin')
    with pytest.raises(AccessDenied):create_user(setup['a'],'evil@example.test','Evil','A-long-viewer-password!','platform_admin')


def test_deactivation_effect_immediate(setup):
    viewer=Principal(create_user(setup['a'],'viewer@example.test','Viewer','A-long-viewer-password!','viewer'))
    set_user_active(setup['a'],viewer.user_id,False)
    with pytest.raises(AccessDenied):assets(viewer)
    set_organisation_active(setup['platform'],setup['org_a'],False)
    with pytest.raises(AccessDenied):assets(setup['a'])


def test_duplicate_asset_transaction_rolls_back(setup):
    with pytest.raises(IntegrityError):create_asset(setup['a'],setup['station_a'],setup['kind'],'T1','Duplicate',transformer={'rating_kva':100,'primary_kv':11,'secondary_kv':0.415})
    assert len(assets(setup['a']))==2


def test_demo_and_alert_lifecycle(setup):
    asset=seed_demo(setup['a'])
    rows=measurements(setup['a']);assert len(rows)==150 and all(x['simulated'] for x in rows)
    proof=evidence(setup['a'],asset)
    assert proof['dga_samples'][0]['gases']['C2H2']=='<1.0'
    alert=alerts(setup['a'])[0]['id']
    with pytest.raises(AccessDenied):record_event(setup['b'],alert,'acknowledge')
    with pytest.raises(ValueError):record_event(setup['a'],alert,'resolve','No evidence')
    first=record_event(setup['a'],alert,'acknowledge',idempotency_key='ack1')
    assert record_event(setup['a'],alert,'acknowledge',idempotency_key='ack1')==first
    with pytest.raises(ValueError):record_event(setup['a'],alert,'acknowledge')
    record_event(setup['a'],alert,'finding','Synthetic inspection verified; training only.')
    record_event(setup['a'],alert,'resolve','Training scenario closed.')
    assert alerts(setup['a'])[0]['status']=='resolved'
    record_event(setup['a'],alert,'evaluate','Clear evidence',5)
    assert len(alert_events(setup['a'],alert))==4
    record_event(setup['a'],alert,'reopen','New evidence')
    record_event(setup['a'],alert,'acknowledge')
    with pytest.raises(ValueError,match='finding'):record_event(setup['a'],alert,'resolve','Old finding cannot close new cycle')
    with pytest.raises(ValueError):seed_demo(setup['a'])


def test_backup_restore(setup):
    add(setup)
    target=backup(setup['tmp']/'backup.sqlite')
    with sqlite3.connect(target) as c:
        assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert c.execute('SELECT count(*) FROM measurements').fetchone()[0]==1
    with pytest.raises(ValueError):backup(target)


def test_bootstrap_not_repeatable(setup):
    with pytest.raises(ValueError):bootstrap('new@example.test','New','Another-long-password!')


def test_demo_atomic_rollback(setup,monkeypatch):
    import modules.monitoring.demo as demo
    original=demo.record_measurement
    count=0
    def failing(*args,**kwargs):
        nonlocal count
        count+=1
        if count==3:raise ValueError('Injected import failure')
        return original(*args,**kwargs)
    monkeypatch.setattr(demo,'record_measurement',failing)
    with pytest.raises(ValueError):demo.seed_demo(setup['a'])
    assert len(assets(setup['a']))==2
    assert measurements(setup['a'])==[]


def test_export_tenant_scope_and_permission(setup):
    add(setup)
    assert len(measurements(setup['a'],export=True))==1
    assert measurements(setup['b'],export=True)==[]
    tech=Principal(create_user(setup['a'],'tech@example.test','Technician','A-long-technician-password!','technician'))
    with pytest.raises(AccessDenied):measurements(tech,export=True)


def test_database_blocks_cross_tenant_actor(setup):
    with pytest.raises(IntegrityError):
        with session_scope() as s:
            s.add(InspectionRecord(organisation_id=setup['org_a'],asset_id=setup['oil'],inspector_id=setup['b'].user_id,inspected_at=utcnow(),inspection_type='Visual',findings='Test',checklist_snapshot={}));s.flush()


def test_platform_cannot_read_tenant_inventory(setup):
    with pytest.raises(AccessDenied):assets(setup['platform'])
