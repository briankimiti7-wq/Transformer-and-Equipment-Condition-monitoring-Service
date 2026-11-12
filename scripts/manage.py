"""Run from project root: python -m scripts.manage init|bootstrap|backup."""
import argparse
import getpass
import sqlite3
from pathlib import Path
from sqlalchemy import select
from alembic.config import Config
from alembic import command
from config.settings import ROOT,database_url
from database.connection import session_scope,get_engine
from database.seed import seed_reference
from database.models import User,Role
from modules.authentication.service import email_normalize,password_hash


def migrate():
    cfg=Config(str(ROOT/'alembic.ini'))
    command.upgrade(cfg,'head')
    seed_reference()


def bootstrap(email,name,password):
    with session_scope() as s:
        if s.scalar(select(User.id).limit(1)):
            raise ValueError('Bootstrap is available only before the first account exists.')
        role=s.scalar(select(Role).where(Role.code=='platform_admin'))
        if not role:raise ValueError('Run init first.')
        row=User(email=email_normalize(email),display_name=name.strip(),password_hash=password_hash(password),role_id=role.id,is_platform_admin=True)
        if not row.display_name:raise ValueError('Name is required.')
        s.add(row);s.flush();return row.id


def backup(destination):
    path=Path(destination).resolve()
    if path.exists():raise ValueError('Backup destination already exists; choose a new filename.')
    dbpath=get_engine().url.database
    if not dbpath or not Path(dbpath).is_file():raise ValueError('SQLite database not found.')
    path.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(dbpath) as source,sqlite3.connect(path) as target:
        source.backup(target)
        result=target.execute('PRAGMA integrity_check').fetchone()[0]
        if result!='ok':raise ValueError('Backup integrity check failed.')
    return path


def main():
    parser=argparse.ArgumentParser(description='TECM database administration')
    parser.add_argument('action',choices=['init','bootstrap','backup'])
    parser.add_argument('--destination')
    args=parser.parse_args()
    if args.action=='init':migrate();print('Schema migrated and reference data ready.')
    elif args.action=='bootstrap':
        email=input('Platform administrator email: ')
        name=input('Display name: ')
        password=getpass.getpass('Password (12+ characters): ')
        if password!=getpass.getpass('Repeat password: '):raise ValueError('Passwords do not match.')
        bootstrap(email,name,password);print('Administrator created. Start Streamlit and sign in.')
    else:
        if not args.destination:parser.error('--destination is required for backup')
        print('Verified backup:',backup(args.destination))

if __name__=='__main__':main()
