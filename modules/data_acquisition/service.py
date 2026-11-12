"""Validated manual observations, with no invented engineering thresholds."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import math
from sqlalchemy import select
from database.connection import session_scope
from database.models import Asset, TransformerDetail, MonitoringParameter, DataSource, Measurement
from database.models.base import utcnow
from modules.authentication.service import require, audit
from modules.assets.service import owned


def parameters(principal):
    with session_scope() as s:
        require(s,principal,'inventory.read')
        return [{'id':p.id,'code':p.code,'name':p.name,'unit':p.canonical_unit,'applicability':p.applicability} for p in s.scalars(select(MonitoringParameter).where(MonitoringParameter.is_active==True))]


def record_measurement(principal, asset_id, parameter_id, value, observed_at, unit, is_simulated=False):
    if not isinstance(observed_at,datetime) or observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError('Observation time must include a timezone.')
    observed_at=observed_at.astimezone(timezone.utc)
    if observed_at>utcnow()+timedelta(minutes=5):raise ValueError('Observation time cannot be in the future.')
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value):raise ValueError('Measurement must be a finite number.')
    with session_scope() as s:
        actor=require(s,principal,'measurement.write')
        asset=owned(s,Asset,asset_id,actor.organisation_id)
        if not asset.is_active:raise ValueError('Asset is inactive.')
        param=s.get(MonitoringParameter,parameter_id)
        if not param or not param.is_active:raise ValueError('Parameter unavailable.')
        if unit!=param.canonical_unit:raise ValueError('Use the parameter canonical unit. Automatic conversion is not enabled in this milestone.')
        detail=s.scalar(select(TransformerDetail).where(TransformerDetail.asset_id==asset.id,TransformerDetail.organisation_id==actor.organisation_id))
        if param.applicability in ['oil_only','dry_only','transformer_all'] and not detail:raise ValueError('This parameter requires a registered transformer.')
        if (param.applicability=='oil_only' and detail.construction!='oil') or (param.applicability=='dry_only' and detail.construction!='dry'):raise ValueError('Parameter is not applicable to this transformer construction.')
        if param.category!='thermal' and value<0:raise ValueError('This parameter cannot be negative.')
        if param.code=='oil_level' and value>100:raise ValueError('Oil level cannot exceed 100%.')
        source_code='simulation' if is_simulated else 'manual'
        source=s.scalar(select(DataSource).where(DataSource.organisation_id==actor.organisation_id,DataSource.code==source_code))
        if not source:
            source=DataSource(organisation_id=actor.organisation_id,code=source_code,name=source_code.title(),source_type=source_code)
            s.add(source);s.flush()
        if not source.is_active:raise ValueError('Data source is inactive.')
        # Same observation identity with a changed value is a conflict, not an overwrite.
        key=sha256(json.dumps([actor.organisation_id,asset_id,parameter_id,observed_at.isoformat(),source.id]).encode()).hexdigest()
        existing=s.scalar(select(Measurement).where(Measurement.organisation_id==actor.organisation_id,Measurement.dedupe_key==key))
        if existing:
            if existing.value!=float(value):raise ValueError('A different value exists at this timestamp. Keep the original record; correction workflow is pending.')
            return existing.id,False
        row=Measurement(organisation_id=actor.organisation_id,asset_id=asset_id,parameter_id=parameter_id,source_id=source.id,recorded_by=actor.id,observed_at=observed_at,recorded_at=utcnow(),value=float(value),unit=unit,raw_value=float(value),raw_unit=unit,quality='unverified',is_simulated=bool(is_simulated),dedupe_key=key)
        s.add(row);s.flush();audit(s,actor,'record','measurements',row.id,{'simulated':bool(is_simulated)})
        return row.id,True
