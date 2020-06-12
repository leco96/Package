from rest_framework import status
from rest_framework_simplejwt.utils import aware_utcnow

from login.models import UserCustom
from django.urls import reverse
from rest_framework.test import APITestCase
from django.test import Client
from rest_framework.authtoken.models import Token
from django.test import TestCase
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken, OutstandingToken,
)
from django.core.management import call_command
from unittest.mock import patch

from allauth.account.models import EmailAddress, EmailConfirmationHMAC, EmailConfirmation


# Create your tests here.
class UserPageTest(APITestCase):

    def test_root_url_resolves_to_users_page(self):
        url = reverse('prueba:my_users-list')
        self.assertEqual(url, '/api/users/')

    def test_create_user(self):
        url = reverse('prueba:my_users-list')
        data = {'username': "user01", 'password': '123', 'first_name': 'david', 'last_name': 'Mora',
                'email': 'example@hotmail.com', 'clave_ciudadano': 'curpExample01', }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserCustom.objects.count(), 1)
        self.assertEqual(UserCustom.objects.get().username, 'user01')

    def test_delete_user(self):
        UserCustom.objects.create(username="admin", password='123', first_name='david', last_name='Mora',
                                  email='example@hotmail.com', clave_ciudadano='curpExample01')
        url = reverse('prueba:my_users-detail', kwargs={'pk': 1})
        self.client.delete(url)


class ApiTest(TestCase):

    def setUp(self):
        self.user = UserCustom.objects.create(username="admin", password='123', first_name='david', last_name='Mora',
                                              email='example@hotmail.com', clave_ciudadano='curpExample01')
        self.token = RefreshToken.for_user(self.user)
        self.c = Client()

    def test_authorization(self):
        header = {'HTTP_AUTHORIZATION': 'Token {}'.format(self.token)}
        response = self.client.get(reverse('prueba:my_users-list'), {}, **header)
        self.assertEqual(response.status_code, 200, "REST token-auth failed")


class TestTokenBlacklistFlushExpiredTokens(TestCase):
    def setUp(self):
        self.user = UserCustom.objects.create(username="admin", password='123', first_name='david', last_name='Mora',
                                              email='example@hotmail.com', clave_ciudadano='curpExample01')

    def test_it_should_delete_any_expired_tokens(self):
        # Make some tokens that won't expire soon
        not_expired_1 = RefreshToken.for_user(self.user)
        not_expired_2 = RefreshToken.for_user(self.user)
        not_expired_3 = RefreshToken()

        # Blacklist fresh tokens
        not_expired_2.blacklist()
        not_expired_3.blacklist()

        # Make tokens with fake exp time that will expire soon
        fake_now = aware_utcnow() - api_settings.REFRESH_TOKEN_LIFETIME

        with patch('rest_framework_simplejwt.tokens.aware_utcnow') as fake_aware_utcnow:
            fake_aware_utcnow.return_value = fake_now
            expired_1 = RefreshToken.for_user(self.user)
            expired_2 = RefreshToken()

        # Blacklist expired tokens
        expired_1.blacklist()
        expired_2.blacklist()

        # Make another token that won't expire soon
        not_expired_4 = RefreshToken.for_user(self.user)

        # Should be certain number of outstanding tokens and blacklisted
        # tokens
        self.assertEqual(OutstandingToken.objects.count(), 6)
        self.assertEqual(BlacklistedToken.objects.count(), 4)

        call_command('flushexpiredtokens')

        # Expired outstanding *and* blacklisted tokens should be gone
        self.assertEqual(OutstandingToken.objects.count(), 4)
        self.assertEqual(BlacklistedToken.objects.count(), 2)

        self.assertEqual(
            [i.jti for i in OutstandingToken.objects.order_by('id')],
            [not_expired_1['jti'], not_expired_2['jti'], not_expired_3['jti'], not_expired_4['jti']],
        )
        self.assertEqual(
            [i.token.jti for i in BlacklistedToken.objects.order_by('id')],
            [not_expired_2['jti'], not_expired_3['jti']],
        )

class CustomSignUpWithDJRestAuth(TestCase):
    def test_FullSignUp(self):
        #Registering a new user
        url_to_signup = '/sso/registration/'
        url_to_verify_key = '/sso/account-confirm-email/'
        data = {'username': "testuser", 'password1': 'optica2020', 'password2': 'optica2020', 'email': 'example@hotmail.com','clave_ciudadano':'123abc'}
        response = self.client.post(url_to_signup, data)
        #verifying the user email
        exist_keyclassgenerator = EmailConfirmationHMAC(EmailAddress.objects.get(email='example@hotmail.com'))
        key = {'key': exist_keyclassgenerator.key}
        self.assertEqual(type(key['key']), type('str'))
        try:
            exist_keyclassgenerator2 = EmailConfirmationHMAC(EmailAddress.objects.get(email='dontexist@hotmail.com'))
            key = {'key': exist_keyclassgenerator2.key}
            self.assertEqual(type(key['key']), type('str'))
        except:
            self.assertEqual('correo no existe', 'correo no existe')
        response1 = self.client.post(url_to_verify_key, key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserCustom.objects.get(id=1).username, data['username'])
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data, {'detail':'ok'})
