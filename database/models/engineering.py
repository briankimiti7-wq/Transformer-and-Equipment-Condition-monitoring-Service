"""SQLAlchemy ORM models for the approved TECM schema."""
from sqlalchemy import Column, String, Float, Integer, Boolean, Date, JSON, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from database.models.base import Base, UTCDateTime, uuid_str, utcnow

class ConditionAssessment(Base):
    __tablename__ = "condition_assessments"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    methodology_id = Column(String, nullable=False)
    sample_id = Column(String, nullable=True)
    assessment_type = Column(String, nullable=False)
    assessed_at = Column(UTCDateTime(), nullable=False)
    assessed_by = Column(String, nullable=True)
    result_status = Column(String, nullable=False)
    evidence_snapshot = Column(JSON, nullable=False)
    limitations = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['methodology_id'], ['assessment_methodologies.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'sample_id'], ['dga_samples.organisation_id', 'dga_samples.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'assessed_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id', 'asset_id'),
        ForeignKeyConstraint(['organisation_id','sample_id','asset_id'], ['dga_samples.organisation_id','dga_samples.id','dga_samples.asset_id'], ondelete='RESTRICT'),
    )

class AssessmentFinding(Base):
    __tablename__ = "assessment_findings"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    assessment_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    statement = Column(String, nullable=False)
    evidence_snapshot = Column(JSON, nullable=False)
    recommended_action = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'assessment_id'], ['condition_assessments.organisation_id', 'condition_assessments.id'], ondelete='RESTRICT'),
    )

class HealthIndex(Base):
    __tablename__ = "health_indices"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    assessment_id = Column(String, nullable=False)
    methodology_id = Column(String, nullable=False)
    calculated_at = Column(UTCDateTime(), nullable=False)
    score = Column(Float, nullable=True)
    classification = Column(String, nullable=False)
    completeness = Column(Float, nullable=False)
    confidence_label = Column(String, nullable=False)
    calculation_snapshot = Column(JSON, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'assessment_id'], ['condition_assessments.organisation_id', 'condition_assessments.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['methodology_id'], ['assessment_methodologies.id'], ondelete='RESTRICT'),
        UniqueConstraint('assessment_id'),
        CheckConstraint('score IS NULL OR score BETWEEN 0 AND 100', name="ck_health_indices_0"),
        CheckConstraint('completeness BETWEEN 0 AND 100', name="ck_health_indices_1"),
        ForeignKeyConstraint(['organisation_id','assessment_id','asset_id'], ['condition_assessments.organisation_id','condition_assessments.id','condition_assessments.asset_id'], ondelete='RESTRICT'),
    )

class FaultRecord(Base):
    __tablename__ = "fault_records"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    assessment_id = Column(String, nullable=True)
    category = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False)
    detected_at = Column(UTCDateTime(), nullable=False)
    detection_method = Column(String, nullable=False)
    evidence_snapshot = Column(JSON, nullable=False)
    recommended_action = Column(String, nullable=True)
    confirmed_by = Column(String, nullable=True)
    confirmed_at = Column(UTCDateTime(), nullable=True)
    resolved_at = Column(UTCDateTime(), nullable=True)
    resolution_note = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'assessment_id'], ['condition_assessments.organisation_id', 'condition_assessments.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'confirmed_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        CheckConstraint("status IN ('indication','confirmed','ruled_out','resolved')", name="ck_fault_records_0"),
        CheckConstraint("status != 'confirmed' OR (confirmed_by IS NOT NULL AND confirmed_at IS NOT NULL)", name="ck_fault_records_1"),
        ForeignKeyConstraint(['organisation_id','assessment_id','asset_id'], ['condition_assessments.organisation_id','condition_assessments.id','condition_assessments.asset_id'], ondelete='RESTRICT'),
    )

class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    parameter_id = Column(String, nullable=True)
    methodology_id = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    window_start = Column(UTCDateTime(), nullable=False)
    window_end = Column(UTCDateTime(), nullable=False)
    generated_at = Column(UTCDateTime(), nullable=False)
    horizon_hours = Column(Float, nullable=True)
    output_snapshot = Column(JSON, nullable=False)
    limitations = Column(String, nullable=False)
    is_simulated = Column(Boolean(create_constraint=True), nullable=False, default=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['parameter_id'], ['monitoring_parameters.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['methodology_id'], ['assessment_methodologies.id'], ondelete='RESTRICT'),
        CheckConstraint('window_end >= window_start', name="ck_prediction_records_0"),
    )

class ParameterLimit(Base):
    __tablename__ = "parameter_limits"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    parameter_id = Column(String, nullable=False)
    asset_type_id = Column(String, nullable=True)
    asset_id = Column(String, nullable=True)
    regime = Column(String, nullable=False)
    applicability = Column(String, nullable=False)
    warning_low = Column(Float, nullable=True)
    warning_high = Column(Float, nullable=True)
    critical_low = Column(Float, nullable=True)
    critical_high = Column(Float, nullable=True)
    unit = Column(String, nullable=False)
    source = Column(String, nullable=False)
    source_edition = Column(String, nullable=True)
    revision = Column(String, nullable=False)
    effective_from = Column(UTCDateTime(), nullable=False)
    effective_to = Column(UTCDateTime(), nullable=True)
    approved_by = Column(String, nullable=False)
    is_demo = Column(Boolean(create_constraint=True), nullable=False, default=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['parameter_id'], ['monitoring_parameters.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['asset_type_id'], ['asset_types.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'approved_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        CheckConstraint('warning_low IS NOT NULL OR warning_high IS NOT NULL OR critical_low IS NOT NULL OR critical_high IS NOT NULL', name="ck_parameter_limits_0"),
        CheckConstraint('effective_to IS NULL OR effective_to > effective_from', name="ck_parameter_limits_1"),
        CheckConstraint('critical_low IS NULL OR warning_low IS NULL OR critical_low <= warning_low', name="ck_parameter_limits_2"),
        CheckConstraint('warning_high IS NULL OR critical_high IS NULL OR warning_high <= critical_high', name="ck_parameter_limits_3"),
        CheckConstraint('warning_low IS NULL OR warning_high IS NULL OR warning_low < warning_high', name="ck_parameter_limits_4"),
    )

class AssessmentMethodology(Base):
    __tablename__ = "assessment_methodologies"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    version = Column(String, nullable=False)
    assessment_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    source = Column(String, nullable=False)
    source_edition = Column(String, nullable=True)
    configuration = Column(JSON, nullable=False)
    validation_status = Column(String, nullable=False)
    effective_from = Column(UTCDateTime(), nullable=False)
    effective_to = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        UniqueConstraint('code', 'version'),
        CheckConstraint("validation_status IN ('draft','validated','retired')", name="ck_assessment_methodologies_0"),
        CheckConstraint('effective_to IS NULL OR effective_to > effective_from', name="ck_assessment_methodologies_1"),
    )

