import unittest

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User

from sqlalchemy.exc import IntegrityError

from project.tests.utils import add_user


class TestUserModel(BaseTestCase):

    def test_add_user(self):
        user = add_user('test', 'test@test.com')
        self.assertTrue(user.id)
        self.assertEqual(user.username, 'test')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.active)

    def test_add_user_duplicate_username(self):
        add_user('test', 'test@test.com')
        duplicate_user = User(username='test', email='test2@test.com')
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_add_user_duplicate_email(self):
        user = add_user('test', 'test@test.com')
        db.session.add(user)
        db.session.commit()
        duplicate_user = User(username='test2', email='test@test.com')
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_to_json(self):
        user = add_user('test', 'test@test.com')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(isinstance(user.to_json(), dict))


if __name__ == '__main__':
    unittest.main()
