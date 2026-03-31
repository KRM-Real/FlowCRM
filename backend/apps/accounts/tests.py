import uuid

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization


class AuthenticationApiTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            email="owner@example.com",
            username="owner",
            password=self.password,
            first_name="Flow",
            last_name="Owner",
        )
        self.organization = Organization.objects.create(
            name="Acme",
            slug="acme",
        )
        Membership.objects.create(
            user=self.user,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )

    def test_register_creates_user_with_uuid_id(self):
        response = self.client.post(
            reverse("auth_register"),
            {
                "email": "new.user@example.com",
                "password": self.password,
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(email="new.user@example.com")
        self.assertIsInstance(created_user.id, uuid.UUID)
        self.assertEqual(response.data["user"]["email"], created_user.email)

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("auth_register"),
            {
                "email": self.user.email,
                "password": self.password,
                "first_name": "Flow",
                "last_name": "Owner",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_sets_auth_cookies(self):
        response = self.client.post(
            reverse("auth_login"),
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.AUTH_COOKIE_ACCESS, response.cookies)
        self.assertIn(settings.AUTH_COOKIE_REFRESH, response.cookies)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_me_returns_authenticated_user_with_memberships(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("auth_me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(len(response.data["memberships"]), 1)
        self.assertEqual(
            response.data["memberships"][0]["organization_id"],
            self.organization.id,
        )

    def test_me_rejects_anonymous_requests(self):
        response = self.client.get(reverse("auth_me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_refresh_cookie(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )
        old_refresh = login_response.cookies[settings.AUTH_COOKIE_REFRESH].value

        response = self.client.post(reverse("auth_refresh"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(settings.AUTH_COOKIE_ACCESS, response.cookies)
        self.assertIn(settings.AUTH_COOKIE_REFRESH, response.cookies)
        self.assertNotEqual(
            response.cookies[settings.AUTH_COOKIE_REFRESH].value,
            old_refresh,
        )

    def test_logout_clears_cookies_and_invalidates_refresh_token(self):
        login_response = self.client.post(
            reverse("auth_login"),
            {
                "email": self.user.email,
                "password": self.password,
            },
            format="json",
        )
        refresh_token = login_response.cookies[settings.AUTH_COOKIE_REFRESH].value

        logout_response = self.client.post(reverse("auth_logout"))

        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(logout_response.cookies[settings.AUTH_COOKIE_ACCESS].value, "")
        self.assertEqual(logout_response.cookies[settings.AUTH_COOKIE_REFRESH].value, "")

        other_client = self.client_class()
        other_client.cookies[settings.AUTH_COOKIE_REFRESH] = refresh_token
        refresh_response = other_client.post(reverse("auth_refresh"))

        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
