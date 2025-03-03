import re
from urllib.parse import urlparse

from django.contrib import auth
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from faker import Faker

User = auth.get_user_model()


class FrontendAuthTest(TestCase):

    def setUp(self):
        self.fake = Faker('de_DE')
        Faker.seed(0)

        self.user = User.objects.create(
            username=self.fake.user_name(),
            first_name=self.fake.first_name(),
            last_name=self.fake.last_name(),
            email=self.fake.email(),
            is_active=True,
        )
        self.user.set_password('pass@123')
        self.user.save()

    def test_user_login(self):
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        login_url = reverse('frontend_auth:login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'username': self.user.username,
            'password': 'pass@123',
        }
        response = self.client.post(login_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    # def test_user_login_next(self):
    #     user = auth.get_user(self.client)
    #     self.assertFalse(user.is_authenticated)
    #
    #     login_url = f"{reverse('frontend_auth:login')}?next=/extsearch/"
    #     response = self.client.get(login_url)
    #     self.assertEqual(response.status_code, 200)
    #
    #     form_data = {
    #         'username': self.user.username,
    #         'password': 'pass@123',
    #     }
    #     response = self.client.post(login_url, form_data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertEqual(response.url, reverse('core:extsearch'))
    #     user = auth.get_user(self.client)
    #     self.assertTrue(user.is_authenticated)

    def test_user_logout(self):
        self.client.force_login(self.user)
        logout_url = reverse('frontend_auth:logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_password_change(self):
        self.client.force_login(self.user)
        pw_change_url = reverse('frontend_auth:password_change')
        response = self.client.get(pw_change_url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'old_password': 'pass@123',
            'new_password1': 'pass*321',
            'new_password2': 'pass*321',
        }
        response = self.client.post(pw_change_url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('frontend_auth:password_change_done'))
        user = auth.get_user(self.client)
        self.assertTrue(user.check_password('pass*321'))

    def test_password_reset(self):
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

        reset_url = reverse('frontend_auth:password_reset')
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'email': self.user.email,
        }
        response = self.client.post(reset_url, form_data)
        self.assertEqual(response.status_code, 302)
        reset_done_url = reverse('frontend_auth:password_reset_done')
        self.assertEqual(response.url, reset_done_url)
        self.assertEqual(len(mail.outbox), 1)

        link = re.search("(?P<url>https?://[^\\s]+)", mail.outbox[0].body).group("url")
        new_pw_url = urlparse(link).path
        response = self.client.get(new_pw_url)
        self.assertEqual(response.status_code, 302)

        form_data = {
            'new_password1': 'pass*321',
            'new_password2': 'pass*321',
        }
        response = self.client.post(response.url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('frontend_auth:password_reset_complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('pass*321'))
