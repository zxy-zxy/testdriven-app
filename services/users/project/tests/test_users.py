import json
import unittest

from project.tests.base import BaseTestCase
from project.tests.utils import add_user
from project import db
from project.api.models import User


class TestUserService(BaseTestCase):

    def authenticate_admin_user(self):
        add_user(
            'authenticated_admin_user',
            'authenticated_admin_user@mail.com',
            'greaterthaneight'
        )
        user = User.query.filter_by(
            email='authenticated_admin_user@mail.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'authenticated_admin_user@mail.com',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json'
            )
            return resp_login

    def authenticate_user(self):
        add_user(
            'authenticated_user',
            'authenticated_user@mail.com',
            'greaterthaneight'
        )
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'authenticated_user@mail.com',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json'
            )
            return resp_login

    def test_main_no_users(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        add_user('test_user', 'test_user@mail.com', 'greaterthaneight')
        add_user('test_user2', 'test_user2@mail.com', 'greaterthaneight')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'test_user', response.data)
            self.assertIn(b'test_user2', response.data)

    def test_main_add_user(self):
        with self.client:
            response = self.client.post(
                '/',
                data=dict(
                    username='test',
                    email='test@mail.com',
                    password='greaterthaneight'
                ),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(b'test', response.data)

    def test_users(self):
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        resp_login = self.authenticate_admin_user()
        auth_token = json.loads(resp_login.data.decode())['auth_token']

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com',
                    'password': 'greaterthaneight',
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('test_user@mail.com was added!', data['message'])

    def test_user_invalid_json(self):
        resp_login = self.authenticate_admin_user()
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_invalid_json_keys(self):
        resp_login = self.authenticate_admin_user()
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'test_user@mail.com'}),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        resp_login = self.authenticate_admin_user()
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com',
                    'password': 'greaterthaneight',
                }),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com',
                    'password': 'greaterthaneight',
                }),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        user = add_user(
            username='test_user',
            email='test_user@mail.com',
            password='greaterthaneight'
        )

        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('test_user', data['data']['username'])
            self.assertIn('test_user@mail.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        with self.client:
            response = self.client.get('/users/foo')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist.', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        add_user(
            username='test_user',
            email='test_user@mail.com',
            password='greaterthaneight',
        )

        add_user(
            username='test_user2',
            email='test_user2@mail.com',
            password='greaterthaneight',
        )

        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('test_user', data['data']['users'][0]['username'])
            self.assertIn(
                'test_user@mail.com',
                data['data']['users'][0]['email'])
            self.assertTrue(data['data']['users'][0]['active'])
            self.assertFalse(data['data']['users'][0]['admin'])
            self.assertIn(
                'test_user2',
                data['data']['users'][1]['username'])
            self.assertIn(
                'test_user2@mail.com',
                data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])
            self.assertTrue(data['data']['users'][1]['active'])
            self.assertFalse(data['data']['users'][1]['admin'])

    def test_add_user_inactive(self):
        add_user('test', 'test@test.com', 'greaterthaneight')
        user = User.query.filter_by(email='test@test.com').first()
        user.active = False
        db.session.commit()

        with self.client:
            response_login = self.client.post(
                '/auth/login',
                data=json.dumps({
                    'email': 'test@test.com',
                    'password': 'greaterthaneight'
                }),
                content_type='application/json'
            )
            auth_token = json.loads(response_login.data.decode())['auth_token']

            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'new_user',
                    'email': 'new_user@mail.com',
                    'password': 'test'
                }),
                content_type='application/json',
                headers={'Authorization': f'Bearer: {auth_token}'},
            )

            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Provide a valid auth token.')
            self.assertEqual(response.status_code, 401)

    def test_add_user_not_admin(self):
        resp_login = self.authenticate_user()
        auth_token = json.loads(resp_login.data.decode())['auth_token']
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test',
                    'email': 'test@test.com',
                    'password': 'greaterthaneight',
                }),
                headers={'Authorization': f'Bearer {auth_token}'},
                content_type='application/json')
            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertIn(
                'You do not have permission to do that.',
                data['message']
            )


if __name__ == '__main__':
    unittest.main()
