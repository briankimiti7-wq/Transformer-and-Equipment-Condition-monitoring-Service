from sqlalchemy import select, update
from database.connection import session_scope
from database.models import Alert, AlertEvent
from database.models.base import utcnow
from modules.assets.service import owned
from modules.authentication.service import require,audit


def record_event(principal,alert_id,action,note='',rating=None,idempotency_key=None):
    if action not in ['acknowledge','verify','handoff','finding','resolve','reopen','evaluate']:raise ValueError('Invalid alert action.')
    permission='feedback.write' if action=='evaluate' else 'alerts.resolve' if action in ['resolve','reopen'] else 'alerts.write'
    if action not in ['acknowledge','evaluate'] and not note.strip():raise ValueError('Describe the evidence or action taken.')
    if len(note)>2000:raise ValueError('Note must be at most 2000 characters.')
    if action=='evaluate' and (type(rating) is not int or not 1<=rating<=5):raise ValueError('Clarity rating must be 1–5.')
    key=idempotency_key or __import__('uuid').uuid4().hex
    with session_scope() as s:
        actor=require(s,principal,permission)
        alert=owned(s,Alert,alert_id,actor.organisation_id)
        old=s.scalar(select(AlertEvent).where(AlertEvent.organisation_id==actor.organisation_id,AlertEvent.idempotency_key==key))
        if old:
            if old.alert_id!=alert_id or old.event_type!=action or old.actor_id!=actor.id:raise ValueError('Idempotency key was already used for a different action.')
            return old.id
        now=utcnow(); changes={}
        if action=='acknowledge':
            if alert.status!='open':raise ValueError('Only open alerts can be acknowledged.')
            changes={'status':'acknowledged','acknowledged_by':actor.id,'acknowledged_at':now}
        elif action=='resolve':
            if alert.status!='acknowledged':raise ValueError('Acknowledge the alert before resolving it.')
            finding=s.scalar(select(AlertEvent.id).where(AlertEvent.organisation_id==actor.organisation_id,AlertEvent.alert_id==alert.id,AlertEvent.event_type=='finding',AlertEvent.occurred_at>=alert.acknowledged_at))
            if not finding:raise ValueError('Record a field finding after acknowledgement before resolving.')
            changes={'status':'resolved','resolved_by':actor.id,'resolved_at':now}
        elif action=='reopen':
            if alert.status!='resolved':raise ValueError('Only resolved alerts can be reopened.')
            changes={'status':'open','acknowledged_by':None,'acknowledged_at':None,'resolved_by':None,'resolved_at':None}
        elif action!='evaluate' and alert.status=='resolved':raise ValueError('Reopen the alert before adding operational actions.')
        # Compare-and-set state and version prevents lost updates from concurrent sessions.
        values={**changes,'updated_at':now}
        result=s.execute(update(Alert).where(Alert.id==alert.id,Alert.organisation_id==actor.organisation_id,Alert.status==alert.status,Alert.updated_at==alert.updated_at).values(**values))
        if result.rowcount!=1:raise ValueError('Alert changed in another session. Refresh and retry.')
        row=AlertEvent(organisation_id=actor.organisation_id,alert_id=alert.id,actor_id=actor.id,event_type=action,occurred_at=now,note=note.strip() or None,clarity_rating=rating if action=='evaluate' else None,idempotency_key=key)
        s.add(row);s.flush();audit(s,actor,action,'alerts',alert.id)
        return row.id
