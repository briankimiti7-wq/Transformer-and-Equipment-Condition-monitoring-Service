"""Account authentication and permission checks, independent of Streamlit."""
from dataclasses import dataclass
from datetime import timedelta
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from sqlalchemy import select
from database.connection import session_scope
from database.models import User, Organisation, Role, Permission, RolePermission, AuditLog
from database.models.base import utcnow

HASHER = PasswordHasher()
DUMMY_HASH = HASHER.hash('not-a-user-password-' + __import__('secrets').token_hex(24))

class AccessDenied(ValueError):
    pass

@dataclass(frozen=True)
class Principal:
    user_id: str


def email_normalize(email):
    email = email.strip().lower()
    if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ValueError('Enter a valid email address.')
    return email


def password_hash(password):
    if not isinstance(password, str) or len(password) < 12 or len(password) > 1024:
        raise ValueError('Use a password of 12–1024 characters.')
    return HASHER.hash(password)


def audit(session, actor, action, entity, entity_id, details=None, organisation_id=None):
    session.add(AuditLog(organisation_id=organisation_id if organisation_id is not None else actor.organisation_id,
        actor_id=actor.id, action=action, entity_type=entity, entity_id=entity_id, occurred_at=utcnow(), details=details or {}))


def require(session, principal, permission):
    user = session.get(User, principal.user_id)
    if not user or not user.is_active:
        raise AccessDenied('Your account is unavailable. Sign in again.')
    if user.organisation_id:
        org = session.get(Organisation, user.organisation_id)
        if not org or not org.is_active:
            raise AccessDenied('Your organisation is inactive.')
    codes = session.scalars(select(Permission.code).join(RolePermission, RolePermission.permission_id == Permission.id).where(RolePermission.role_id == user.role_id)).all()
    if permission not in codes:
        raise AccessDenied('Your account does not have permission for this action.')
    return user


def authenticate(email, password):
    # Failed-attempt updates commit before returning an error.
    principal = None
    try:
        normal = email_normalize(email)
    except ValueError:
        normal = ''
    with session_scope() as s:
        user = s.scalar(select(User).where(User.email == normal))
        now = utcnow()
        locked = user and user.locked_until and user.locked_until > now
        valid = False
        try:
            valid = HASHER.verify(user.password_hash if user and not locked else DUMMY_HASH, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            pass
        org = s.get(Organisation, user.organisation_id) if user and user.organisation_id else None
        if user and valid and not locked and user.is_active and (user.is_platform_admin or (org and org.is_active)):
            user.failed_attempts = 0
            user.locked_until = None
            user.last_login_at = now
            if HASHER.check_needs_rehash(user.password_hash):
                user.password_hash = HASHER.hash(password)
            audit(s, user, 'login', 'users', user.id)
            principal = Principal(user.id)
        elif user and not locked:
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
                user.failed_attempts = 0
    if not principal:
        raise AccessDenied('Sign-in failed. Check your credentials or retry after the account lock expires.')
    return principal


def profile(principal):
    with session_scope() as s:
        user = require(s, principal, 'profile.read')
        role = s.get(Role, user.role_id)
        org = s.get(Organisation, user.organisation_id) if user.organisation_id else None
        return {'id': user.id, 'name': user.display_name, 'role': role.code, 'organisation_id': user.organisation_id,
                'organisation': org.name if org else 'Platform administration', 'platform': user.is_platform_admin}


def permissions(principal):
    with session_scope() as s:
        user = require(s, principal, 'profile.read')
        return set(s.scalars(select(Permission.code).join(RolePermission, RolePermission.permission_id == Permission.id).where(RolePermission.role_id == user.role_id)).all())


def create_user(principal, email, display_name, password, role_code):
    hashed = password_hash(password)
    email = email_normalize(email)
    with session_scope() as s:
        actor = require(s, principal, 'users.manage')
        role = s.scalar(select(Role).where(Role.code == role_code))
        if not actor.organisation_id or not role or role.code == 'platform_admin':
            raise AccessDenied('Only organisation roles can be assigned here.')
        if not display_name.strip():
            raise ValueError('Display name is required.')
        user = User(organisation_id=actor.organisation_id, role_id=role.id, email=email,
                    display_name=display_name.strip(), password_hash=hashed)
        s.add(user); s.flush()
        audit(s, actor, 'create', 'users', user.id, {'role': role_code})
        return user.id


def list_users(principal):
    with session_scope() as s:
        actor = require(s, principal, 'users.manage')
        return [{'id': u.id, 'name': u.display_name, 'email': u.email, 'active': u.is_active, 'role': s.get(Role,u.role_id).code}
                for u in s.scalars(select(User).where(User.organisation_id == actor.organisation_id))]


def set_user_active(principal, user_id, active):
    with session_scope() as s:
        actor = require(s, principal, 'users.manage')
        user = s.scalar(select(User).where(User.id == user_id, User.organisation_id == actor.organisation_id))
        if not user or user.id == actor.id:
            raise AccessDenied('Cannot change this account here.')
        user.is_active = bool(active)
        audit(s, actor, 'activation', 'users', user.id, {'active': active})
