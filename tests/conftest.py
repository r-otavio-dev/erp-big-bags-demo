import pytest
from app import create_app, db

@pytest.fixture()
def app(tmp_path):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(tmp_path/'test.db').as_posix()}"})
    yield app
    with app.app_context(): db.session.remove(); db.drop_all()

