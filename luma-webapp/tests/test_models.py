"""
tests/test_models.py — Issue #2: extended DB models
"""

from app import db
from app.models import User, Asset, Job


def test_user_new_fields_default_to_none(app):
    with app.app_context():
        user = User(username="u", email="u@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.avatar_url is None
        assert user.last_login_at is None
        assert repr(user) == f"<User id={user.id} username='u'>"


def test_login_sets_last_login_at(client):
    from tests.conftest import register, login

    register(client, username="u2", email="u2@example.com")
    login(client, email="u2@example.com")

    with client.application.app_context():
        user = User.query.filter_by(username="u2").first()
        assert user.last_login_at is not None


def test_job_has_prompt_and_asset_relationship(app):
    with app.app_context():
        user = User(username="u3", email="u3@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        asset = Asset(user_id=user.id, filename="a.png", prompt="a cat")
        db.session.add(asset)
        db.session.commit()

        job = Job(user_id=user.id, prompt="a cat", status="done", result_asset_id=asset.id)
        db.session.add(job)
        db.session.commit()

        assert job.prompt == "a cat"
        assert job.result_asset.id == asset.id
        assert repr(job) == f"<Job id={job.id} user_id={user.id} status='done'>"
        assert repr(asset) == f"<Asset id={asset.id} user_id={user.id} filename='a.png'>"
