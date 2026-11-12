"""SQLAlchemy ORM models for the approved TECM schema."""
from sqlalchemy import Column, String, Float, Integer, Boolean, Date, JSON, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from database.models.base import Base, UTCDateTime, uuid_str, utcnow

class MonitoringParameter(Base):
    __tablename__ = "monitoring_parameters"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    canonical_unit = Column(String, nullable=False)
    category = Column(String, nullable=False)
    applicability = Column(String, nullable=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        UniqueConstraint('code'),
    )

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        UniqueConstraint('organisation_id', 'code'),
        CheckConstraint("source_type IN ('manual','csv','excel','sensor','scada','simulation')", name="ck_data_sources_0"),
    )

class DataImportBatch(Base):
    __tablename__ = "data_import_batches"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_sha256 = Column(String, nullable=False)
    stored_path = Column(String, nullable=True)
    status = Column(String, nullable=False)
    total_rows = Column(Integer, nullable=False, default=0)
    accepted_rows = Column(Integer, nullable=False, default=0)
    rejected_rows = Column(Integer, nullable=False, default=0)
    duplicate_rows = Column(Integer, nullable=False, default=0)
    mapping_snapshot = Column(JSON, nullable=False)
    confirmed_at = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'source_id'], ['data_sources.organisation_id', 'data_sources.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'uploaded_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id', 'source_id'),
        CheckConstraint('total_rows >= 0 AND accepted_rows >= 0 AND rejected_rows >= 0 AND duplicate_rows >= 0', name="ck_data_import_batches_0"),
        CheckConstraint("status IN ('preview','validated','importing','completed','failed')", name="ck_data_import_batches_1"),
        CheckConstraint("status != 'completed' OR total_rows = accepted_rows + rejected_rows + duplicate_rows", name="ck_data_import_batches_2"),
    )

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    parameter_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    protocol = Column(String, nullable=True)
    installed_at = Column(UTCDateTime(), nullable=True)
    communication_status = Column(String, nullable=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['parameter_id'], ['monitoring_parameters.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'code'),
        UniqueConstraint('organisation_id', 'id', 'asset_id', 'parameter_id'),
    )

class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    parameter_id = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    sensor_id = Column(String, nullable=True)
    batch_id = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)
    observed_at = Column(UTCDateTime(), nullable=False)
    recorded_at = Column(UTCDateTime(), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    raw_value = Column(Float, nullable=False)
    raw_unit = Column(String, nullable=False)
    quality = Column(String, nullable=False)
    is_simulated = Column(Boolean(create_constraint=True), nullable=False, default=False)
    external_record_id = Column(String, nullable=True)
    dedupe_key = Column(String, nullable=False)
    supersedes_id = Column(String, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['parameter_id'], ['monitoring_parameters.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'source_id'], ['data_sources.organisation_id', 'data_sources.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'sensor_id'], ['sensors.organisation_id', 'sensors.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'batch_id'], ['data_import_batches.organisation_id', 'data_import_batches.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'recorded_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'supersedes_id'], ['measurements.organisation_id', 'measurements.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'dedupe_key'),
        UniqueConstraint('organisation_id', 'id', 'asset_id', 'parameter_id'),
        Index("ix_measurements_0", 'organisation_id', 'asset_id', 'parameter_id', 'observed_at'),
        Index("ix_measurements_1", 'organisation_id', 'batch_id'),
        ForeignKeyConstraint(['organisation_id','sensor_id','asset_id','parameter_id'], ['sensors.organisation_id','sensors.id','sensors.asset_id','sensors.parameter_id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id','batch_id','source_id'], ['data_import_batches.organisation_id','data_import_batches.id','data_import_batches.source_id'], ondelete='RESTRICT'),
    )

class DGASample(Base):
    __tablename__ = "dga_samples"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    source_id = Column(String, nullable=False)
    batch_id = Column(String, nullable=True)
    recorded_by = Column(String, nullable=True)
    sample_reference = Column(String, nullable=False)
    sampled_at = Column(UTCDateTime(), nullable=False)
    laboratory = Column(String, nullable=True)
    method = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_simulated = Column(Boolean(create_constraint=True), nullable=False, default=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'source_id'], ['data_sources.organisation_id', 'data_sources.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'batch_id'], ['data_import_batches.organisation_id', 'data_import_batches.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['organisation_id', 'recorded_by'], ['users.organisation_id', 'users.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'asset_id', 'sample_reference'),
        UniqueConstraint('organisation_id', 'id', 'asset_id'),
        Index("ix_dga_samples_0", 'organisation_id', 'asset_id', 'sampled_at'),
    )

class DGAGasMeasurement(Base):
    __tablename__ = "dga_gas_measurements"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    sample_id = Column(String, nullable=False)
    gas_code = Column(String, nullable=False)
    concentration_ppm = Column(Float, nullable=True)
    qualifier = Column(String, nullable=False)
    detection_limit_ppm = Column(Float, nullable=True)
    quality = Column(String, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'sample_id'], ['dga_samples.organisation_id', 'dga_samples.id'], ondelete='RESTRICT'),
        UniqueConstraint('sample_id', 'gas_code'),
        CheckConstraint("gas_code IN ('H2','CH4','C2H6','C2H4','C2H2','CO','CO2')", name="ck_dga_gas_measurements_0"),
        CheckConstraint("qualifier IN ('measured','below_limit','not_measured')", name="ck_dga_gas_measurements_1"),
        CheckConstraint('concentration_ppm IS NULL OR concentration_ppm >= 0', name="ck_dga_gas_measurements_2"),
        CheckConstraint('detection_limit_ppm IS NULL OR detection_limit_ppm >= 0', name="ck_dga_gas_measurements_3"),
        CheckConstraint("qualifier != 'measured' OR concentration_ppm IS NOT NULL", name="ck_dga_gas_measurements_4"),
        CheckConstraint("qualifier != 'below_limit' OR detection_limit_ppm IS NOT NULL", name="ck_dga_gas_measurements_5"),
    )

class ImportRowError(Base):
    __tablename__ = "import_row_errors"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    batch_id = Column(String, nullable=False)
    row_number = Column(Integer, nullable=False)
    column_name = Column(String, nullable=True)
    error_code = Column(String, nullable=False)
    message = Column(String, nullable=False)
    raw_row = Column(JSON, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'batch_id'], ['data_import_batches.organisation_id', 'data_import_batches.id'], ondelete='RESTRICT'),
        CheckConstraint('row_number > 0', name="ck_import_row_errors_0"),
    )

