from project import db
from project.api.models import User


def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def add_admin(username, email, password):
    user = User(
        username=username, email=email,
        password=password, admin=True
    )
    db.session.add(user)
    db.session.commit()
    return user
