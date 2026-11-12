"""Tenant-owned inventory transactions and platform provisioning."""
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal
from database.connection import session_scope
from database.models import Organisation, User, Role, Substation, Asset, AssetType, TransformerDetail, DataSource
from modules.authentication.service import require, audit, password_hash, email_normalize, AccessDenied

class TransformerInput(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    application: Literal['power','distribution'] = 'distribution'
    construction: Literal['oil','dry'] = 'oil'
    rating_kva: float = Field(gt=0)
    primary_kv: float = Field(gt=0)
    secondary_kv: float = Field(gt=0)
    phases: Literal[1,3] = 3
    frequency_hz: float = Field(default=50,gt=0)
    vector_group: str | None = None
    cooling: str | None = None
    insulation_class: str | None = None
    impedance_percent: float | None = Field(default=None,gt=0)
    tap_changer_type: str | None = None
    rated_primary_a: float | None = Field(default=None,gt=0)
    rated_secondary_a: float | None = Field(default=None,gt=0)
    oil_volume_l: float | None = Field(default=None,ge=0)


def text_required(value, label):
    if not isinstance(value,str) or not value.strip() or len(value)>250:
        raise ValueError(f'{label} must contain 1–250 characters.')
    return value.strip()


def owned(s, model, item_id, org):
    if not org:
        raise AccessDenied('An organisation account is required.')
    row=s.scalar(select(model).where(model.id==item_id,model.organisation_id==org))
    if not row:
        raise AccessDenied('Record not found in your organisation.')
    return row


def create_organisation(principal, code, name, country, admin_email, admin_name, admin_password):
    hashed=password_hash(admin_password)
    normal=email_normalize(admin_email)
    with session_scope() as s:
        actor=require(s,principal,'platform.manage')
        org=Organisation(code=text_required(code,'Code').upper(),name=text_required(name,'Name'),country=text_required(country,'Country'))
        s.add(org);s.flush()
        role=s.scalar(select(Role).where(Role.code=='organisation_admin'))
        user=User(organisation_id=org.id,role_id=role.id,email=normal,display_name=text_required(admin_name,'Administrator name'),password_hash=hashed)
        s.add(user);s.flush()
        # Platform action audited in platform scope; target tenant recorded in details.
        audit(s,actor,'provision','organisations',org.id,{'target_organisation':org.id})
        return org.id


def organisations(principal):
    with session_scope() as s:
        require(s,principal,'platform.manage')
        return [{'id':o.id,'code':o.code,'name':o.name,'country':o.country,'active':o.is_active} for o in s.scalars(select(Organisation))]


def set_organisation_active(principal, organisation_id, active):
    with session_scope() as s:
        actor=require(s,principal,'platform.manage')
        org=s.get(Organisation,organisation_id)
        if not org:raise ValueError('Organisation not found.')
        org.is_active=bool(active)
        audit(s,actor,'activation','organisations',org.id,{'active':active})


def create_substation(principal, code, name, location, voltage_kv):
    if not __import__('math').isfinite(voltage_kv) or voltage_kv<=0:raise ValueError('Voltage must be positive.')
    with session_scope() as s:
        actor=require(s,principal,'inventory.write')
        row=Substation(organisation_id=actor.organisation_id,code=text_required(code,'Code').upper(),name=text_required(name,'Name'),location=text_required(location,'Location'),voltage_kv=voltage_kv,status='Operational')
        s.add(row);s.flush();audit(s,actor,'create','substations',row.id)
        return row.id


def catalogues(principal):
    with session_scope() as s:
        require(s,principal,'inventory.read')
        return [{'id':a.id,'code':a.code,'name':a.name} for a in s.scalars(select(AssetType).where(AssetType.is_active==True))]


def substations(principal):
    with session_scope() as s:
        actor=require(s,principal,'inventory.read')
        return [{'id':a.id,'code':a.code,'name':a.name,'location':a.location,'voltage_kv':a.voltage_kv} for a in s.scalars(select(Substation).where(Substation.organisation_id==actor.organisation_id,Substation.is_active==True))]


def create_asset(principal, substation_id, type_id, code, name, manufacturer='', serial_number='', criticality='Medium', transformer=None):
    if criticality not in ['Low','Medium','High','Critical']:raise ValueError('Invalid criticality.')
    with session_scope() as s:
        actor=require(s,principal,'inventory.write')
        station=owned(s,Substation,substation_id,actor.organisation_id)
        kind=s.get(AssetType,type_id)
        if not station.is_active or not kind or not kind.is_active:raise ValueError('Choose active inventory records.')
        if kind.code=='transformer':
            if transformer is None:raise ValueError('Transformer nameplate details are required.')
            details=TransformerInput.model_validate(transformer)
            if details.construction=='dry' and details.oil_volume_l is not None:raise ValueError('Oil volume is not applicable to dry-type transformers.')
        elif transformer is not None:raise ValueError('Transformer details require a Transformer asset.')
        row=Asset(organisation_id=actor.organisation_id,substation_id=station.id,asset_type_id=kind.id,code=text_required(code,'Asset code').upper(),name=text_required(name,'Asset name'),manufacturer=manufacturer or None,serial_number=serial_number or None,status='In service',criticality=criticality)
        s.add(row);s.flush()
        if kind.code=='transformer':s.add(TransformerDetail(organisation_id=actor.organisation_id,asset_id=row.id,**details.model_dump()))
        audit(s,actor,'create','assets',row.id)
        return row.id


def assets(principal):
    with session_scope() as s:
        actor=require(s,principal,'inventory.read')
        rows=s.execute(select(Asset,AssetType,Substation).join(AssetType,Asset.asset_type_id==AssetType.id).join(Substation,Asset.substation_id==Substation.id).where(Asset.organisation_id==actor.organisation_id,Asset.is_active==True)).all()
        result=[]
        for a,t,station in rows:
            detail=s.scalar(select(TransformerDetail).where(TransformerDetail.asset_id==a.id,TransformerDetail.organisation_id==actor.organisation_id))
            result.append({'id':a.id,'code':a.code,'name':a.name,'type':t.name,'type_code':t.code,'substation':station.name,'status':a.status,'criticality':a.criticality,'construction':detail.construction if detail else None,'rating_kva':detail.rating_kva if detail else None,'primary_kv':detail.primary_kv if detail else None,'secondary_kv':detail.secondary_kv if detail else None})
        return result
