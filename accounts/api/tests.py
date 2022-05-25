from rest_framework.test import APIClient
from testing.testcases import TestCase

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    def test_login(self):
        # login only allow POST
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # login fail, http status code return 405
        self.assertEqual(response.status_code, 405)

        # use post method, but wrong password
        response = self.client.post(LOGIN_URL,  {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test if not login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # use correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        # test already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # test user already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test GET method
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # test POST method
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # test user already logout
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # test GET failure
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # test password too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        # test username too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is toooooooooooooooooo loooooooooooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # SIGNUP successfully
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # test user login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


