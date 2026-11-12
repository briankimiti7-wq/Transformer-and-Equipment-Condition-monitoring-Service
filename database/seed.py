"""Idempotent reference data only. No users or passwords are seeded."""
from sqlalchemy import select
from database.connection import session_scope
from database.models import Role, Permission, RolePermission, AssetType, MonitoringParameter

PERMISSIONS = ['profile.read','platform.manage','users.manage','inventory.read','inventory.write','measurement.write','alerts.write','alerts.resolve','feedback.write','maintenance.write','reports.read']
ROLE_GRANTS = {
 'platform_admin': ['profile.read','platform.manage'],
 'organisation_admin': [p for p in PERMISSIONS if p != 'platform.manage'],
 'electrical_engineer': ['profile.read','inventory.read','inventory.write','measurement.write','alerts.write','alerts.resolve','feedback.write','reports.read'],
 'maintenance_engineer': ['profile.read','inventory.read','measurement.write','alerts.write','alerts.resolve','maintenance.write','feedback.write','reports.read'],
 'technician': ['profile.read','inventory.read','measurement.write','alerts.write','maintenance.write','feedback.write'],
 'viewer': ['profile.read','inventory.read','feedback.write','reports.read'],
}
PARAMETERS = [
 ('top_oil','Top-oil temperature','°C','thermal','oil_only'),
 ('winding','Winding temperature','°C','thermal','transformer_all'),
 ('ambient','Ambient temperature','°C','thermal','transformer_all'),
 ('primary_voltage','Primary voltage','kV','electrical','transformer_all'),
 ('secondary_voltage','Secondary voltage','kV','electrical','transformer_all'),
 ('primary_current','Primary current','A','electrical','transformer_all'),
 ('secondary_current','Secondary current','A','electrical','transformer_all'),
 ('loading','Loading','%','loading','transformer_all'),
 ('oil_level','Oil level','%','oil','oil_only'),
 ('moisture','Oil moisture','mg/kg','oil','oil_only'),
 ('insulation_resistance','Insulation resistance','MΩ','insulation','transformer_all'),
 ('polarisation_index','Polarisation index','ratio','insulation','transformer_all'),
 ('breakdown_voltage','Oil breakdown voltage','kV','oil','oil_only'),
 ('tan_delta','Dissipation factor','%','insulation','transformer_all'),
]

def seed_reference():
    with session_scope() as s:
        for code in PERMISSIONS:
            if not s.scalar(select(Permission).where(Permission.code == code)):
                s.add(Permission(code=code, description=code.replace('.',' ')))
        for code in ROLE_GRANTS:
            if not s.scalar(select(Role).where(Role.code == code)):
                s.add(Role(code=code, name=code.replace('_',' ').title()))
        s.flush()
        for code,grants in ROLE_GRANTS.items():
            role=s.scalar(select(Role).where(Role.code==code))
            for grant in grants:
                permission=s.scalar(select(Permission).where(Permission.code==grant))
                if not s.get(RolePermission,(role.id,permission.id)):
                    s.add(RolePermission(role_id=role.id,permission_id=permission.id))
        for code,name in [('transformer','Transformer'),('generator','Generator'),('breaker','Circuit breaker'),('relay','Protection relay'),('motor','Motor'),('battery','Battery'),('cable','Cable'),('switchgear','Switchgear'),('tap_changer','Tap changer')]:
            if not s.scalar(select(AssetType).where(AssetType.code==code)):
                s.add(AssetType(code=code,name=name,analytics_supported=code=='transformer'))
        for code,name,unit,category,app in PARAMETERS:
            if not s.scalar(select(MonitoringParameter).where(MonitoringParameter.code==code)):
                s.add(MonitoringParameter(code=code,name=name,canonical_unit=unit,category=category,applicability=app))
