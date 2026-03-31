from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization


class OrganizationMembershipApiTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="StrongPass123!",
        )
        self.member_user = User.objects.create_user(
            email="member@example.com",
            username="member",
            password="StrongPass123!",
        )
        self.outsider_user = User.objects.create_user(
            email="outsider@example.com",
            username="outsider",
            password="StrongPass123!",
        )
        self.organization = Organization.objects.create(name="Acme", slug="acme")

        self.admin_membership = Membership.objects.create(
            user=self.admin_user,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            user=self.member_user,
            organization=self.organization,
            role=Membership.Role.REP,
        )

    def test_member_can_list_organization_members(self):
        self.client.force_authenticate(self.member_user)

        response = self.client.get(
            reverse(
                "organization-members",
                kwargs={"organization_id": self.organization.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_non_member_cannot_list_other_organization_members(self):
        self.client.force_authenticate(self.outsider_user)

        response = self.client.get(
            reverse(
                "organization-members",
                kwargs={"organization_id": self.organization.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_membership(self):
        new_user = User.objects.create_user(
            email="newmember@example.com",
            username="newmember",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            reverse(
                "organization-members",
                kwargs={"organization_id": self.organization.id},
            ),
            {
                "user_id": str(new_user.id),
                "role": Membership.Role.MANAGER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Membership.objects.filter(
                user=new_user,
                organization=self.organization,
                role=Membership.Role.MANAGER,
            ).exists()
        )

    def test_non_admin_cannot_create_membership(self):
        new_user = User.objects.create_user(
            email="another@example.com",
            username="another",
            password="StrongPass123!",
        )
        self.client.force_authenticate(self.member_user)

        response = self.client.post(
            reverse(
                "organization-members",
                kwargs={"organization_id": self.organization.id},
            ),
            {
                "user_id": str(new_user.id),
                "role": Membership.Role.REP,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_remove_last_admin(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.delete(
            reverse(
                "organization-member-detail",
                kwargs={
                    "organization_id": self.organization.id,
                    "pk": self.admin_membership.id,
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
