from django.test import TestCase
from django.contrib.auth  import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

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


    def test_retrieve_user_unauthrized(self):
        """ Test that authentication is required for users """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPITests(TestCase):
    """ Tests User API tjat requrie authentication (Private) """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email = 'test@mail.com', password = 'hgyr74yfr',
            name = 'King'
            )
        self.client.force_authenticate(user = self.user)


    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)



        def test_update_user_profile(self):
            """ Test the profile upadate of authenticated user"""
            payload ={
                 'name': 'Upated name',
                 'password': 'Newpassword',
                 'email': 'Updaed email'
             }
            res = self.client.patch('ME_URL',payload)
            self.user.refresh_from_db()
            self.assertEqual(self.user.name,payload['name'])
            self.assertEqual(self.user.email,payload['email'])
            self.assertTrue(self.user.check_password( payload['password']))
            self.assertEqual(res.status_code, status.HTTP_200_OK)

            res = self.client.get('ME_URL')

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual( res.data, {
                'name': self.user.name,
                'email': self.user.email
            })
