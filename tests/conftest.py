import pytest
from sqlalchemy import select
from database.connection import session_scope,engine_for
from database.models import User,AssetType
from scripts.manage import migrate,bootstrap
from modules.authentication.service import Principal
from modules.assets.service import create_organisation,create_substation,create_asset

@pytest.fixture
def setup(tmp_path,monkeypatch):
    monkeypatch.setenv('TECM_DATABASE_URL','sqlite:///'+(tmp_path/'test.db').as_posix())
    migrate()
    platform=Principal(bootstrap('platform@example.test','Platform','A-long-test-password!'))
    org_a=create_organisation(platform,'ORG-A','Organisation A','Kenya','admin-a@example.test','Admin A','A-long-test-password!')
    org_b=create_organisation(platform,'ORG-B','Organisation B','Kenya','admin-b@example.test','Admin B','B-long-test-password!')
    with session_scope() as s:
        a=Principal(s.scalar(select(User).where(User.email=='admin-a@example.test')).id)
        b=Principal(s.scalar(select(User).where(User.email=='admin-b@example.test')).id)
        kind=s.scalar(select(AssetType).where(AssetType.code=='transformer')).id
    station_a=create_substation(a,'S1','Station A','Nairobi',33)
    station_b=create_substation(b,'S1','Station B','Athi River',33)
    oil=create_asset(a,station_a,kind,'T1','Oil transformer',transformer={'rating_kva':1000,'primary_kv':11,'secondary_kv':0.415,'construction':'oil'})
    dry=create_asset(a,station_a,kind,'T2','Dry transformer',transformer={'rating_kva':1000,'primary_kv':11,'secondary_kv':0.415,'construction':'dry'})
    asset_b=create_asset(b,station_b,kind,'T1','Other tenant transformer',transformer={'rating_kva':500,'primary_kv':11,'secondary_kv':0.415})
    yield dict(platform=platform,a=a,b=b,org_a=org_a,org_b=org_b,station_a=station_a,station_b=station_b,oil=oil,dry=dry,asset_b=asset_b,kind=kind,tmp=tmp_path)
    engine_for.cache_clear()
