from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.leads.models import Lead, LeadStatus
from apps.organizations.models import Membership, Organization


class LeadApiTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            username="admin",
            password="StrongPass123!",
        )
        self.manager_user = User.objects.create_user(
            email="manager@example.com",
            username="manager",
            password="StrongPass123!",
        )
        self.rep_user = User.objects.create_user(
            email="rep@example.com",
            username="rep",
            password="StrongPass123!",
        )
        self.outsider_user = User.objects.create_user(
            email="outsider@example.com",
            username="outsider",
            password="StrongPass123!",
        )

        self.organization = Organization.objects.create(name="Acme", slug="acme")
        self.other_organization = Organization.objects.create(name="Beta", slug="beta")

        Membership.objects.create(
            user=self.admin_user,
            organization=self.organization,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            user=self.manager_user,
            organization=self.organization,
            role=Membership.Role.MANAGER,
        )
        Membership.objects.create(
            user=self.rep_user,
            organization=self.organization,
            role=Membership.Role.REP,
        )
        Membership.objects.create(
            user=self.outsider_user,
            organization=self.other_organization,
            role=Membership.Role.ADMIN,
        )

        self.org_lead = Lead.objects.create(
            organization=self.organization,
            created_by=self.admin_user,
            name="Acme Lead",
            email="lead@acme.com",
            status=LeadStatus.NEW,
        )
        self.other_org_lead = Lead.objects.create(
            organization=self.other_organization,
            created_by=self.outsider_user,
            name="Beta Lead",
            email="lead@beta.com",
            status=LeadStatus.NEW,
        )

    def test_member_can_list_only_own_organization_leads(self):
        self.client.force_authenticate(self.rep_user)

        response = self.client.get(
            reverse("lead-list-create", kwargs={"organization_id": self.organization.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], str(self.org_lead.id))

    def test_non_member_cannot_access_other_organization_leads(self):
        self.client.force_authenticate(self.outsider_user)

        response = self.client.get(
            reverse("lead-list-create", kwargs={"organization_id": self.organization.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_lead(self):
        self.client.force_authenticate(self.manager_user)

        response = self.client.post(
            reverse("lead-list-create", kwargs={"organization_id": self.organization.id}),
            {
                "name": "Qualified Lead",
                "email": "qualified@example.com",
                "status": LeadStatus.QUALIFIED,
                "source": "MANUAL",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Lead.objects.filter(
                organization=self.organization,
                email="qualified@example.com",
            ).exists()
        )

    def test_rep_cannot_create_lead(self):
        self.client.force_authenticate(self.rep_user)

        response = self.client.post(
            reverse("lead-list-create", kwargs={"organization_id": self.organization.id}),
            {
                "name": "Blocked Lead",
                "email": "blocked@example.com",
                "status": LeadStatus.NEW,
                "source": "MANUAL",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lead_detail_is_scoped_to_route_organization(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(
            reverse(
                "lead-detail",
                kwargs={
                    "organization_id": self.organization.id,
                    "pk": self.other_org_lead.id,
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
