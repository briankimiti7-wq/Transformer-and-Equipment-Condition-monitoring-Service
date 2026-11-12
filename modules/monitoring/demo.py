"""Explicitly requested synthetic fixtures, separate from field measurements."""
from datetime import timedelta
from sqlalchemy import select
from database.connection import session_scope
from database.models import *
from database.models.base import utcnow
from modules.authentication.service import require,audit
from modules.assets.service import create_substation,create_asset
from modules.data_acquisition.service import record_measurement


def seed_demo(principal):
    with session_scope():
        return _seed_demo(principal)


def _seed_demo(principal):
    with session_scope() as s:
        actor=require(s,principal,'users.manage')
        if s.scalar(select(Asset.id).where(Asset.organisation_id==actor.organisation_id,Asset.code.like('DEMO-%'))):
            raise ValueError('Demonstration assets already exist. Sample loading is intentionally one-time.')
        kind=s.scalar(select(AssetType).where(AssetType.code=='transformer')).id
    station=create_substation(principal,'DEMO-NN','Nairobi North — synthetic','Synthetic Kenyan substation',132)
    oil=create_asset(principal,station,kind,'DEMO-T1','Main transformer T1 — synthetic',manufacturer='Synthetic fixture',criticality='High',transformer={'rating_kva':45000,'primary_kv':132,'secondary_kv':33,'application':'power','construction':'oil','cooling':'ONAN/ONAF','vector_group':'YNd11'})
    dry=create_asset(principal,station,kind,'DEMO-T2','Distribution T2 — synthetic',manufacturer='Synthetic fixture',transformer={'rating_kva':1000,'primary_kv':11,'secondary_kv':0.415,'application':'distribution','construction':'dry','cooling':'AN'})
    with session_scope() as s:
        pars={p.code:(p.id,p.canonical_unit) for p in s.scalars(select(MonitoringParameter))}
    end=utcnow().replace(minute=0,second=0,microsecond=0)
    for index in range(25):
        when=end-timedelta(hours=24-index)
        for asset,code,value in [(oil,'top_oil',62+index),(oil,'winding',76+index),(oil,'loading',60+index),(oil,'ambient',24+(index%6)),(dry,'winding',65+index%8),(dry,'loading',45+index%12)]:
            pid,unit=pars[code]
            record_measurement(principal,asset,pid,float(value),when,unit,True)
    with session_scope() as s:
        actor=require(s,principal,'users.manage');org=actor.organisation_id
        source=s.scalar(select(DataSource).where(DataSource.organisation_id==org,DataSource.code=='simulation'))
        sample=DGASample(organisation_id=org,asset_id=oil,source_id=source.id,recorded_by=actor.id,sample_reference='DEMO-DGA-01',sampled_at=end-timedelta(days=1),laboratory='Synthetic example',method='Sample data only; no diagnostic method applied',is_simulated=True)
        s.add(sample);s.flush()
        for gas,value in [('H2',142),('CH4',31),('C2H6',12),('C2H4',24),('C2H2',None),('CO',290),('CO2',2400)]:
            s.add(DGAGasMeasurement(organisation_id=org,sample_id=sample.id,gas_code=gas,concentration_ppm=value,qualifier='measured' if value is not None else 'below_limit',detection_limit_ppm=1 if value is None else None,quality='synthetic'))
        s.add(InspectionRecord(organisation_id=org,asset_id=oil,inspector_id=actor.id,inspected_at=end-timedelta(days=2),inspection_type='Synthetic cooling inspection',findings='SYNTHETIC: fan bank 2 intermittent.',checklist_snapshot={'synthetic':True,'radiators':'clear','fan_bank_2':'intermittent'},recommendations='Training scenario only: verify cooling status.'))
        s.add(MaintenanceRecord(organisation_id=org,asset_id=oil,performed_by=actor.id,performed_at=end-timedelta(days=1),activity_type='Synthetic maintenance log',findings='SYNTHETIC: intermittent fan contactor.',actions_taken='SYNTHETIC: control circuit inspected; follow-up pending.',next_due_on=(end+timedelta(days=7)).date()))
        s.add(RelayEvent(organisation_id=org,asset_id=oil,source_id=source.id,occurred_at=end-timedelta(hours=2),recorded_at=utcnow(),protection_function='49',event_type='Synthetic thermal alarm',breaker_state='Closed',evidence_snapshot={'synthetic':True,'note':'Associated protection event; no actual trip occurred.'},is_simulated=True))
        alert=Alert(organisation_id=org,asset_id=oil,severity='Warning',title='Synthetic cooling investigation',message='Training scenario: rising temperatures with an intermittent fan finding. No validated diagnostic threshold has been applied.',evidence_snapshot={'synthetic':True,'sample_reference':'DEMO-DGA-01','note':'Review seeded inspection and temperature history; not a confirmed fault.'},rule_revision='synthetic-scenario-v1',dedupe_key='demo-cooling-v1',triggered_at=end,status='open')
        s.add(alert);s.flush();audit(s,actor,'seed_demo','assets',oil,{'synthetic':True})
    return oil
