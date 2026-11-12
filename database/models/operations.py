"""SQLAlchemy ORM models for the approved TECM schema."""
from sqlalchemy import Column, String, Float, Integer, Boolean, Date, JSON, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from database.models.base import Base, UTCDateTime, uuid_str, utcnow

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    work_order_id = Column(String, nullable=True)
    performed_by = Column(String, nullable=True)
    performed_at = Column(UTCDateTime(), nullable=False)
    activity_type = Column(String, nullable=False)
    findings = Column(String, nullable=False)
    actions_taken = Column(String, nullable=False)
    replaced_components = Column(String, nullable=True)
    next_due_on = Column(Date, nullable=True)
    source_reference = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'work_order_id'], ['work_orders.organisation_id', 'work_orders.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'performed_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id','work_order_id','asset_id'], ['work_orders.organisation_id','work_orders.id','work_orders.asset_id'], ondelete='RESTRICT'),
    )

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, nullable=False)
    assigned_to = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    due_on = Column(Date, nullable=True)
    started_at = Column(UTCDateTime(), nullable=True)
    completed_at = Column(UTCDateTime(), nullable=True)
    cancelled_at = Column(UTCDateTime(), nullable=True)
    cancellation_reason = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'assigned_to'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'created_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'code'),
        UniqueConstraint('organisation_id', 'id', 'asset_id'),
        CheckConstraint("status IN ('Open','Assigned','In Progress','Completed','Cancelled')", name="ck_work_orders_0"),
        CheckConstraint("status != 'Completed' OR completed_at IS NOT NULL", name="ck_work_orders_1"),
        CheckConstraint("status != 'Cancelled' OR cancellation_reason IS NOT NULL", name="ck_work_orders_2"),
        Index("ix_work_orders_0", 'organisation_id', 'status', 'due_on'),
    )

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    assessment_id = Column(String, nullable=True)
    fault_id = Column(String, nullable=True)
    work_order_id = Column(String, nullable=True)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    evidence_snapshot = Column(JSON, nullable=False)
    rule_revision = Column(String, nullable=False)
    dedupe_key = Column(String, nullable=False)
    triggered_at = Column(UTCDateTime(), nullable=False)
    status = Column(String, nullable=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(UTCDateTime(), nullable=True)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'assessment_id'], ['condition_assessments.organisation_id', 'condition_assessments.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'fault_id'], ['fault_records.organisation_id', 'fault_records.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'work_order_id'], ['work_orders.organisation_id', 'work_orders.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'acknowledged_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'resolved_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'dedupe_key'),
        CheckConstraint("status IN ('open','acknowledged','resolved')", name="ck_alerts_0"),
        CheckConstraint("severity IN ('Information','Warning','Critical')", name="ck_alerts_1"),
        CheckConstraint("status != 'acknowledged' OR (acknowledged_by IS NOT NULL AND acknowledged_at IS NOT NULL)", name="ck_alerts_2"),
        CheckConstraint("status != 'resolved' OR (resolved_by IS NOT NULL AND resolved_at IS NOT NULL)", name="ck_alerts_3"),
        Index("ix_alerts_0", 'organisation_id', 'status', 'severity', 'triggered_at'),
    )

class Report(Base):
    __tablename__ = "reports"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=True)
    substation_id = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    format = Column(String, nullable=False)
    period_start = Column(UTCDateTime(), nullable=True)
    period_end = Column(UTCDateTime(), nullable=True)
    status = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    file_sha256 = Column(String, nullable=True)
    scope_snapshot = Column(JSON, nullable=False)
    generated_at = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'substation_id'], ['substations.organisation_id', 'substations.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'created_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=True)
    actor_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=True)
    occurred_at = Column(UTCDateTime(), nullable=False)
    details = Column(JSON, nullable=False)
    request_id = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'actor_id'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='RESTRICT'),
        Index("ix_audit_logs_0", 'organisation_id', 'occurred_at'),
    )

class AlertEvent(Base):
    __tablename__ = "alert_events"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    alert_id = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    occurred_at = Column(UTCDateTime(), nullable=False)
    note = Column(String, nullable=True)
    outcome = Column(String, nullable=True)
    clarity_rating = Column(Integer, nullable=True)
    idempotency_key = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'alert_id'], ['alerts.organisation_id', 'alerts.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'actor_id'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'idempotency_key'),
        CheckConstraint('clarity_rating IS NULL OR clarity_rating BETWEEN 1 AND 5', name="ck_alert_events_0"),
        CheckConstraint("event_type IN ('acknowledge','verify','handoff','finding','resolve','reopen','evaluate')", name="ck_alert_events_1"),
    )

class InspectionRecord(Base):
    __tablename__ = "inspection_records"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    work_order_id = Column(String, nullable=True)
    inspector_id = Column(String, nullable=True)
    inspected_at = Column(UTCDateTime(), nullable=False)
    inspection_type = Column(String, nullable=False)
    findings = Column(String, nullable=False)
    checklist_snapshot = Column(JSON, nullable=False)
    recommendations = Column(String, nullable=True)
    external_reference = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'work_order_id'], ['work_orders.organisation_id', 'work_orders.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'inspector_id'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id','work_order_id','asset_id'], ['work_orders.organisation_id','work_orders.id','work_orders.asset_id'], ondelete='RESTRICT'),
    )

class RelayEvent(Base):
    __tablename__ = "relay_events"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    batch_id = Column(String, nullable=True)
    occurred_at = Column(UTCDateTime(), nullable=False)
    recorded_at = Column(UTCDateTime(), nullable=False)
    protection_function = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    breaker_state = Column(String, nullable=True)
    phase = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    evidence_snapshot = Column(JSON, nullable=False)
    external_record_id = Column(String, nullable=True)
    is_simulated = Column(Boolean(create_constraint=True), nullable=False, default=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'source_id'], ['data_sources.organisation_id', 'data_sources.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'batch_id'], ['data_import_batches.organisation_id', 'data_import_batches.id'], ondelete='RESTRICT'),
        Index("ix_relay_events_0", 'organisation_id', 'asset_id', 'occurred_at'),
    )

class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    alert_id = Column(String, nullable=False)
    recipient_user_id = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    status = Column(String, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    last_attempt_at = Column(UTCDateTime(), nullable=True)
    sent_at = Column(UTCDateTime(), nullable=True)
    error_summary = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'alert_id'], ['alerts.organisation_id', 'alerts.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'recipient_user_id'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'idempotency_key'),
        CheckConstraint('attempts >= 0', name="ck_notification_deliveries_0"),
        CheckConstraint("status IN ('pending','sent','failed','cancelled')", name="ck_notification_deliveries_1"),
    )

