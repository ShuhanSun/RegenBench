import unittest
from dataclasses import fields

from generated.user_model import User


class UserModelTest(unittest.TestCase):
    def test_email_verified_field_exists(self):
        names = [f.name for f in fields(User)]
        self.assertIn("email_verified", names)

    def test_email_verified_is_usable(self):
        user = User(id=1, name="Ada", email_verified=True)
        self.assertTrue(user.email_verified)


if __name__ == "__main__":
    unittest.main()
