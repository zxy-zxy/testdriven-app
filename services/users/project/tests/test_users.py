import json
import unittest

from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestUserService(BaseTestCase):

    def test_main_no_users(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertIn(b'<p>No users!</p>', response.data)

    def test_main_with_users(self):
        add_user('test_user', 'test_user@mail.com')
        add_user('test_user2', 'test_user2@mail.com')
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
                data=dict(username='test', email='test@mail.com'),
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
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('test_user@mail.com was added!', data['message'])

    def test_user_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_user_invalid_json_keys(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': 'test_user@mail.com'}),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com'
                }),
                content_type='application/json',
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': 'test_user',
                    'email': 'test_user@mail.com'
                }),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        user = add_user(
            username='test_user', email='test_user@mail.com')

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
            email='test_user@mail.com')

        add_user(
            username='test_user2',
            email='test_user2@mail.com')

        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn('test_user', data['data']['users'][0]['username'])
            self.assertIn(
                'test_user@mail.com',
                data['data']['users'][0]['email'])
            self.assertIn(
                'test_user2',
                data['data']['users'][1]['username'])
            self.assertIn(
                'test_user2@mail.com',
                data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])


if __name__ == '__main__':
    unittest.main()
