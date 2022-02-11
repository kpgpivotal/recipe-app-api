from django.test import TestCase
from django.contrib.auth  import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserAPITests(TestCase):
    """ Tests User API (Public) """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test user with valid payload is successfull """
        payload = {
            'email':'test@mail.com',
            'password':'hgyr74yfr',
            'name': 'His Highness Kishore'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_exists(self):
        """ Test creating an already existing  user to fail  """
        payload = {
            'email':'test@mail.com',
            'password':'hgyr74yfr',
            'name': 'His Highness Kishore'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is more than 5 chars """
        payload = {
            'email':'test@mail.com',
            'password':'1234'
            }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)


    def test_crate_token_for_user(self):
        """Test that a token is created for the user  """
        payload = { 'email':'test@mail.com', 'password':'hgyr74yfr',  }
        create_user(**payload)
        res = self.client.post(TOKEN_URL,payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_crate_token_invalid_creds(self):
        """Test that a token is not created when invalid creds are passed  """
        payload = { 'email':'test@mail.com', 'password':'hgyr74yfr',  }
        create_user(**payload)
        payload['password']='wrong'
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crate_token_no_user(self):
        """Test that a token is not created if user doesn't exist  """
        payload = {  'password':'hgyr74yfr',  }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crate_token_no_password(self):
        """Test that a token is not created when password is not passed  """
        payload = { 'email':'test@mail.com', 'password':'',  }
        res = self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
