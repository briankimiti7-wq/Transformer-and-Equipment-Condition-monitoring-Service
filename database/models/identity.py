"""SQLAlchemy ORM models for the approved TECM schema."""
from sqlalchemy import Column, String, Float, Integer, Boolean, Date, JSON, ForeignKeyConstraint, UniqueConstraint, CheckConstraint, Index
from database.models.base import Base, UTCDateTime, uuid_str, utcnow

class Organisation(Base):
    __tablename__ = "organisations"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=False)
    address = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    __table_args__ = (
        UniqueConstraint('code'),
    )

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    organisation_id = Column(String, nullable=True)
    role_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean(create_constraint=True), nullable=False, default=True)
    is_platform_admin = Column(Boolean(create_constraint=True), nullable=False, default=False)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(UTCDateTime(), nullable=True)
    last_login_at = Column(UTCDateTime(), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='RESTRICT'),
        UniqueConstraint('organisation_id', 'id'),
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='RESTRICT'),
        UniqueConstraint('email'),
        CheckConstraint('organisation_id IS NOT NULL OR is_platform_admin = 1', name="ck_users_0"),
        CheckConstraint('failed_attempts >= 0', name="ck_users_1"),
    )

class Role(Base):
    __tablename__ = "roles"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    __table_args__ = (
        UniqueConstraint('code'),
    )

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(String(36), primary_key=True, default=uuid_str)
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    __table_args__ = (
        UniqueConstraint('code'),
    )

class RolePermission(Base):
    __tablename__ = "role_permissions"
    created_at = Column(UTCDateTime(), nullable=False, default=utcnow)
    updated_at = Column(UTCDateTime(), nullable=False, default=utcnow, onupdate=utcnow)
    role_id = Column(String, nullable=False, primary_key=True)
    permission_id = Column(String, nullable=False, primary_key=True)
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='RESTRICT'),
        ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='RESTRICT'),
    )

