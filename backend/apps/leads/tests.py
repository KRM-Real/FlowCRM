from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.leads.models import Lead, LeadSource, LeadStatus
from apps.organizations.models import Membership, Organization

User = get_user_model()


class LeadAPITests(APITestCase):
    def setUp(self):
        self.org_1 = Organization.objects.create(
            name="Org One",
            slug="org-one",
        )
        self.org_2 = Organization.objects.create(
            name="Org Two",
            slug="org-two",
        )

        self.rep_user = User.objects.create_user(
            email="rep@example.com",
            username="repuser",
            password="testpass123",
        )
        self.manager_user = User.objects.create_user(
            email="manager@example.com",
            username="manageruser",
            password="testpass123",
        )
        self.outsider_user = User.objects.create_user(
            email="outsider@example.com",
            username="outsideruser",
            password="testpass123",
        )

        Membership.objects.create(
            user=self.rep_user,
            organization=self.org_1,
            role=Membership.Role.REP,
        )
        Membership.objects.create(
            user=self.manager_user,
            organization=self.org_1,
            role=Membership.Role.MANAGER,
        )
        Membership.objects.create(
            user=self.outsider_user,
            organization=self.org_2,
            role=Membership.Role.REP,
        )

    def list_url(self, organization_id):
        return f"/api/organizations/{organization_id}/leads/"

    def detail_url(self, organization_id, lead_id):
        return f"/api/organizations/{organization_id}/leads/{lead_id}/"

    def test_member_can_list_leads_in_own_organization(self):
        Lead.objects.create(
            organization=self.org_1,
            created_by=self.manager_user,
            name="Lead One",
            email="lead1@example.com",
            source=LeadSource.MANUAL,
            status=LeadStatus.NEW,
        )
        Lead.objects.create(
            organization=self.org_1,
            created_by=self.manager_user,
            name="Lead Two",
            email="lead2@example.com",
            source=LeadSource.FACEBOOK,
            status=LeadStatus.CONTACTED,
        )
        Lead.objects.create(
            organization=self.org_2,
            created_by=self.outsider_user,
            name="Other Org Lead",
            email="other@example.com",
            source=LeadSource.WEBSITE,
            status=LeadStatus.NEW,
        )

        self.client.force_authenticate(user=self.rep_user)
        response = self.client.get(self.list_url(self.org_1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        returned_names = [lead["name"] for lead in response.data["results"]]
        self.assertIn("Lead One", returned_names)
        self.assertIn("Lead Two", returned_names)
        self.assertNotIn("Other Org Lead", returned_names)

    def test_member_cannot_create_lead(self):
        payload = {
            "name": "Blocked Lead",
            "email": "blocked@example.com",
            "phone": "09123456789",
            "source": LeadSource.MANUAL,
            "status": LeadStatus.NEW,
        }

        self.client.force_authenticate(user=self.rep_user)
        response = self.client.post(self.list_url(self.org_1.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lead.objects.filter(name="Blocked Lead").count(), 0)

    def test_manager_can_create_lead(self):
        payload = {
            "name": "Created Lead",
            "email": "created@example.com",
            "phone": "09999999999",
            "source": LeadSource.FACEBOOK,
            "status": LeadStatus.NEW,
        }

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.post(self.list_url(self.org_1.id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 1)

        lead = Lead.objects.get(name="Created Lead")
        self.assertEqual(lead.organization, self.org_1)
        self.assertEqual(lead.created_by, self.manager_user)
        self.assertEqual(lead.source, LeadSource.FACEBOOK)
        self.assertEqual(lead.status, LeadStatus.NEW)

    def test_cross_organization_access_is_blocked(self):
        Lead.objects.create(
            organization=self.org_2,
            created_by=self.outsider_user,
            name="Org Two Lead",
            email="orgtow@example.com",
            source=LeadSource.MANUAL,
            status=LeadStatus.NEW,
        )

        self.client.force_authenticate(user=self.rep_user)
        response = self.client.get(self.list_url(self.org_2.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtering_by_status_and_source_works(self):
        Lead.objects.create(
            organization=self.org_1,
            created_by=self.manager_user,
            name="Lead A",
            email="a@example.com",
            source=LeadSource.MANUAL,
            status=LeadStatus.NEW,
        )
        Lead.objects.create(
            organization=self.org_1,
            created_by=self.manager_user,
            name="Lead B",
            email="b@example.com",
            source=LeadSource.FACEBOOK,
            status=LeadStatus.CONTACTED,
        )
        Lead.objects.create(
            organization=self.org_1,
            created_by=self.manager_user,
            name="Lead C",
            email="c@example.com",
            source=LeadSource.MANUAL,
            status=LeadStatus.NEW,
        )

        self.client.force_authenticate(user=self.rep_user)
        response = self.client.get(
            self.list_url(self.org_1.id),
            {"status": LeadStatus.NEW, "source": LeadSource.MANUAL},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

        returned_names = [lead["name"] for lead in response.data["results"]]
        self.assertEqual(set(returned_names), {"Lead A", "Lead C"})

    def test_pagination_returns_paginated_response_shape(self):
        for i in range(11):
            Lead.objects.create(
                organization=self.org_1,
                created_by=self.manager_user,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                source=LeadSource.MANUAL,
                status=LeadStatus.NEW,
            )

        self.client.force_authenticate(user=self.rep_user)
        response = self.client.get(self.list_url(self.org_1.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        self.assertEqual(response.data["count"], 11)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])