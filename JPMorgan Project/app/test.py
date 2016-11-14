import unittest
import app

class MyTest(unittest.TestCase):
    # create an app
    def setUp(self):
        self.app = app.app.test_client()
        self.app.usernameAndPassword = {'TestUserName':'TestPassword'}

    def test_show_homepage(self):
        response = self.app.get("/")
        assert response.status_code == 200

    def login(self, username, password):
        return self.app.post('/login', data=dict(
        username = username,
        password = password
    ))

    def test_log_in_username_not_exist(self):
        username = 'WrongUserName'
        password = 'TestPassword'
        response = self.login(username, password)
        assert 'User name does not exist.' in response.data

    def test_log_in_password_wrong(self):
        username = 'wangxucan'
        password = 'WrongPassword'
        response = self.login(username, password)
        assert 'Invalid credentials. Please try again.' in response.data

    def test_log_in_success(self):
        username = 'wangxucan'
        password = 'xw2401'
        response = self.login(username, password)
        assert response.status_code == 200

    def test_log_out_success(self):
        response = self.app.get("/logout")
        assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
