from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email succcessfully """
        email = 'king@gmail.com'
        password = 'secret'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test a new user with normalized email """
        email = 'king@Gmail.com'
        user = get_user_model().objects.create_user(email, 'RANDOM')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test a new user with invalid  email raises error """
        with self.assertRaises(ValueError):
            email = None
            get_user_model().objects.create_user(email, 'RANDOM')

    def test_create_new_super_user(self):
        """Test crating a super user """
        email = 'king@Gmail.com'
        user = get_user_model().objects.create_superuser(email, 'RANDOM')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
