from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.leads.models import Lead
from apps.leads.serializers import LeadSerializer
from apps.leads.services import create_lead, update_lead
from apps.leads.selectors import (
    get_leads_by_organization,
    get_lead_by_id,
)
from apps.organizations.models import Organization
from apps.organizations.permissions import BaseOrganizationPermission


class LeadViewSet(viewsets.ViewSet):
    permission_classes = [BaseOrganizationPermission]

    def get_organization(self):
        organization_id = self.kwargs.get("organization_id")
        return Organization.objects.filter(id=organization_id).first()

    def list(self, request, organization_id=None):
        organization = self.get_organization()

        leads = get_leads_by_organization(organization=organization)

        serializer = LeadSerializer(leads, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, organization_id=None):
        organization = self.get_organization()

        lead = get_lead_by_id(
            lead_id=pk,
            organization=organization,
        )

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeadSerializer(lead)
        return Response(serializer.data)

    def create(self, request, organization_id=None):
        organization = self.get_organization()

        serializer = LeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lead = create_lead(
            organization=organization,
            created_by=request.user,
            **serializer.validated_data,
        )

        return Response(
            LeadSerializer(lead).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, pk=None, organization_id=None):
        organization = self.get_organization()

        lead = get_lead_by_id(
            lead_id=pk,
            organization=organization,
        )

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeadSerializer(
            lead,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        updated_lead = update_lead(
            lead=lead,
            **serializer.validated_data,
        )

        return Response(LeadSerializer(updated_lead).data)

    def destroy(self, request, pk=None, organization_id=None):
        organization = self.get_organization()

        lead = get_lead_by_id(
            lead_id=pk,
            organization=organization,
        )

        if not lead:
            return Response(
                {"detail": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lead.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)