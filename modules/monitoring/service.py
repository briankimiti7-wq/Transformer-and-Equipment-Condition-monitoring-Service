"""Read models: authorisation is checked on every call."""
from sqlalchemy import select
from database.connection import session_scope
from database.models import Measurement, MonitoringParameter, Asset, Alert, AlertEvent, InspectionRecord, RelayEvent, MaintenanceRecord, WorkOrder, DGASample, DGAGasMeasurement
from modules.authentication.service import require
from modules.assets.service import owned


def measurements(principal,asset_id=None,start=None,end=None,export=False):
    with session_scope() as s:
        actor=require(s,principal,'reports.read' if export else 'inventory.read')
        q=select(Measurement,MonitoringParameter,Asset).join(MonitoringParameter,Measurement.parameter_id==MonitoringParameter.id).join(Asset,Measurement.asset_id==Asset.id).where(Measurement.organisation_id==actor.organisation_id)
        if asset_id:
            owned(s,Asset,asset_id,actor.organisation_id)
            q=q.where(Measurement.asset_id==asset_id)
        if start:q=q.where(Measurement.observed_at>=start)
        if end:q=q.where(Measurement.observed_at<=end)
        return [{'id':m.id,'asset':a.code,'asset_id':a.id,'parameter':p.name,'parameter_code':p.code,'value':m.value,'unit':m.unit,'observed_at':m.observed_at,'recorded_at':m.recorded_at,'quality':m.quality,'simulated':m.is_simulated} for m,p,a in s.execute(q.order_by(Measurement.observed_at).limit(100000))]


def alerts(principal):
    with session_scope() as s:
        actor=require(s,principal,'inventory.read')
        return [{'id':a.id,'asset_id':a.asset_id,'title':a.title,'severity':a.severity,'message':a.message,'status':a.status,'triggered_at':a.triggered_at,'acknowledged_at':a.acknowledged_at,'evidence':a.evidence_snapshot} for a in s.scalars(select(Alert).where(Alert.organisation_id==actor.organisation_id).order_by(Alert.triggered_at.desc()))]


def alert_events(principal,alert_id):
    with session_scope() as s:
        actor=require(s,principal,'inventory.read');owned(s,Alert,alert_id,actor.organisation_id)
        return [{'action':e.event_type,'at':e.occurred_at,'actor_id':e.actor_id,'note':e.note,'rating':e.clarity_rating} for e in s.scalars(select(AlertEvent).where(AlertEvent.organisation_id==actor.organisation_id,AlertEvent.alert_id==alert_id).order_by(AlertEvent.occurred_at))]


def evidence(principal,asset_id):
    with session_scope() as s:
        actor=require(s,principal,'inventory.read');owned(s,Asset,asset_id,actor.organisation_id)
        result={}
        fields={InspectionRecord:('inspected_at','inspection_type','findings','recommendations','checklist_snapshot'),RelayEvent:('occurred_at','protection_function','event_type','breaker_state','is_simulated','evidence_snapshot'),MaintenanceRecord:('performed_at','activity_type','findings','actions_taken','next_due_on')}
        for model,columns in fields.items():
            result[model.__tablename__]=[{k:getattr(x,k) for k in columns} for x in s.scalars(select(model).where(model.organisation_id==actor.organisation_id,model.asset_id==asset_id))]
        samples=[]
        for sample in s.scalars(select(DGASample).where(DGASample.organisation_id==actor.organisation_id,DGASample.asset_id==asset_id).order_by(DGASample.sampled_at)):
            gases=s.scalars(select(DGAGasMeasurement).where(DGAGasMeasurement.organisation_id==actor.organisation_id,DGAGasMeasurement.sample_id==sample.id)).all()
            samples.append({'reference':sample.sample_reference,'sampled_at':sample.sampled_at,'laboratory':sample.laboratory,'simulated':sample.is_simulated,'gases':{g.gas_code:(g.concentration_ppm if g.qualifier=='measured' else '<'+str(g.detection_limit_ppm) if g.qualifier=='below_limit' else 'not measured') for g in gases}})
        result['dga_samples']=samples
        return result
