import unittest
from flask_testing import TestCase
import app

class tradeAPITestCase(unittest.TestCase):
    def create_app(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True


    def test_show_homepage(self):
        self.app.get('/')
        self.assert_template_used('homepage.html')



if __name__ == '__main__':
    unittest.main()









