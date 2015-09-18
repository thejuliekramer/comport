#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Shell, Server, prompt_bool, prompt_pass
from flask_migrate import MigrateCommand, upgrade


from comport.app import create_app
from comport.user.models import User, Role
from comport.charts.models import ChartBlockDefaults
from comport.department.models import Department, Extractor
from comport.settings import DevConfig, ProdConfig
from comport.database import db
from comport.utils import random_string, parse_date
from comport.data.models import UseOfForceIncident
from tests.factories import UseOfForceIncidentFactory
import json
import csv

if os.environ.get("COMPORT_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User, 'Department': Department, 'Extractor': Extractor, 'UseOfForceIncident': UseOfForceIncident}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '-x', '--verbose'])
    return exit_code


@manager.command
def make_admin_user():
    password = prompt_pass("Password")
    user = User.create(username="admin", email="email@example.com",password=password,active=True)
    admin_role = Role(name='admin')
    admin_role.save()
    user.roles.append(admin_role)
    user.save()

@manager.command
def load_test_data():
    add_chart_block_defaults()
    department = Department.query.filter_by(name="Busy Town Public Safety").first()
    if not department:
        department = Department.create(name="Busy Town Public Safety")
    if not User.query.filter_by(username="user").first():
        User.create(username="user", email="email2@example.com",password="password",active=True, department_id=department.id)
    with open('comport/testData/UOF.csv', 'rt') as f:
        reader = csv.DictReader(f)
        for incident in reader:
            occured_date = parse_date(incident["OCCURRED_DT"])
            UseOfForceIncident.create(opaque_id=random_string(6),
                service_type=incident["SERVICE_TYPE"],
                occured_date=occured_date,
                use_of_force_reason=incident["UOF_REASON"],
                census_tract=None,
                department_id=department.id)

@manager.command
def make_test_data():
    add_chart_block_defaults()
    department = Department.query.filter_by(name="Busy Town Public Safety").first()
    if not department:
        department = Department.create(name="Busy Town Public Safety")

    if not User.query.filter_by(username="user").first():
        User.create(username="user", email="email2@example.com",password="password",active=True, department_id=department.id)
    for _ in range(100):
        incident = UseOfForceIncidentFactory()
        incident.department_id = department.id
        incident.save()

@manager.command
def delete_everything():
   db.reflect()
   db.drop_all()
   upgrade()

@manager.command
def add_chart_block_defaults():
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'data/chartBlockDefaults.json')
    with open(filename) as chart_block_data_file:
        defaults = json.load(chart_block_data_file)
        for default in defaults:
            ChartBlockDefaults.create(title=default["title"],
                caption=default["caption"],
                slug=default["slug"],
                dataset=default["dataset"],
                content=default["content"])


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
