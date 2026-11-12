from pathlib import Path
from streamlit.testing.v1 import AppTest
from modules.monitoring.demo import seed_demo
from modules.authentication.service import create_user

APP=Path(__file__).resolve().parents[1]/'app.py'

def login(email='admin-a@example.test',password='A-long-test-password!'):
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    assert not at.exception
    at.text_input[0].set_value(email)
    at.text_input[1].set_value(password)
    at.button[0].click().run()
    return at


def test_login_inventory_measurement_ui(setup):
    at=login();assert not at.exception
    assert at.title[0].value=='Asset condition overview'
    at.sidebar.radio[0].set_value('Measurements').run()
    assert not at.exception
    at.number_input[0].set_value(72.5)
    next(b for b in at.button if b.label=='Save measurement').click().run()
    assert not at.exception and at.success
    at.sidebar.radio[0].set_value('Asset register').run()
    assert not at.exception
    next(b for b in at.button if b.label=='Sign out').click().run()
    assert any(b.label=='Sign in' for b in at.button)
    assert not at.dataframe


def test_demo_dashboard_all_pages(setup):
    seed_demo(setup['a'])
    at=login();assert not at.exception
    for page in ['Asset register','Substations','Measurements','Evidence','Alerts','Users','Sample data','Overview']:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, (page,list(at.exception))
    for view in ['Operations','Maintenance','Supervisor','Asset / reliability']:
        at.selectbox[0].set_value(view).run()
        assert not at.exception


def test_viewer_ui_has_no_mutations(setup):
    create_user(setup['a'],'view@example.test','Viewer','A-long-viewer-password!','viewer')
    at=login('view@example.test','A-long-viewer-password!')
    assert not at.exception
    assert 'Users' not in at.sidebar.radio[0].options
    at.sidebar.radio[0].set_value('Measurements').run()
    assert not at.exception
    assert not any(b.label=='Save measurement' for b in at.button)


def test_platform_ui(setup):
    at=login('platform@example.test','A-long-test-password!')
    assert not at.exception
    assert any(t.value=='Organisation administration' for t in at.title)
