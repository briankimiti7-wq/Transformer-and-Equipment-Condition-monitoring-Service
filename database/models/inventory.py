"""SQLAlchemy ORM models for the approved TECM schema."""
from sqlalchemy import Column, String, Float, Integer, Boolean, Date, JSON, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from database.models.base import Base, UTCDateTime, uuid_str, utcnow

class Substation(Base):
    __tablename__ = "substations"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    voltage_kv = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        UniqueConstraint('organisation_id', 'code'),
        CheckConstraint('voltage_kv IS NULL OR voltage_kv > 0', name="ck_substations_0"),
        CheckConstraint('latitude IS NULL OR latitude BETWEEN -90 AND 90', name="ck_substations_1"),
        CheckConstraint('longitude IS NULL OR longitude BETWEEN -180 AND 180', name="ck_substations_2"),
    )

class AssetType(Base):
    __tablename__ = "asset_types"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    analytics_supported = Column(Boolean(create_constraint=True), nullable=False, default=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        UniqueConstraint('code'),
    )

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    substation_id = Column(String, nullable=False)
    asset_type_id = Column(String, nullable=False)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    manufactured_year = Column(Integer, nullable=True)
    installed_on = Column(Date, nullable=True)
    commissioned_on = Column(Date, nullable=True)
    status = Column(String, nullable=False)
    criticality = Column(String, nullable=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'substation_id'], ['substations.organisation_id', 'substations.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['asset_type_id'], ['asset_types.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'code'),
        CheckConstraint("criticality IN ('Low','Medium','High','Critical')", name="ck_assets_0"),
    )

class TransformerDetail(Base):
    __tablename__ = "transformer_details"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=False)
    asset_id = Column(String, nullable=False)
    application = Column(String, nullable=False)
    construction = Column(String, nullable=False)
    rating_kva = Column(Float, nullable=False)
    primary_kv = Column(Float, nullable=False)
    secondary_kv = Column(Float, nullable=False)
    phases = Column(Integer, nullable=False)
    frequency_hz = Column(Float, nullable=False)
    vector_group = Column(String, nullable=True)
    cooling = Column(String, nullable=True)
    insulation_class = Column(String, nullable=True)
    impedance_percent = Column(Float, nullable=True)
    tap_changer_type = Column(String, nullable=True)
    rated_primary_a = Column(Float, nullable=True)
    rated_secondary_a = Column(Float, nullable=True)
    oil_volume_l = Column(Float, nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['organisation_id', 'asset_id'], ['assets.organisation_id', 'assets.id'], ondelete='RESTRICT'),
        UniqueConstraint('asset_id'),
        CheckConstraint("application IN ('power','distribution')", name="ck_transformer_details_0"),
        CheckConstraint("construction IN ('oil','dry')", name="ck_transformer_details_1"),
        CheckConstraint('rating_kva > 0 AND primary_kv > 0 AND secondary_kv > 0 AND frequency_hz > 0', name="ck_transformer_details_2"),
        CheckConstraint('phases IN (1,3)', name="ck_transformer_details_3"),
        CheckConstraint("construction != 'dry' OR oil_volume_l IS NULL", name="ck_transformer_details_4"),
        CheckConstraint('oil_volume_l IS NULL OR oil_volume_l >= 0', name="ck_transformer_details_5"),
    )

