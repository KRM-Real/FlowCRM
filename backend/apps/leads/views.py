from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.mixins import OrganizationContextMixin
from apps.common.pagination import DefaultPagination
from apps.leads.selectors import get_lead_by_id, get_leads_by_organization
from apps.leads.serializers import LeadSerializer
from apps.leads.services import create_lead, update_lead
from apps.organizations.permissions import (
    IsOrganizationManagerOrAdmin,
    IsOrganizationMember,
)


class LeadViewSet(OrganizationContextMixin, viewsets.ViewSet):
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated, IsOrganizationMember]
        elif self.action in ["create", "partial_update"]:
            permission_classes = [IsAuthenticated, IsOrganizationManagerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def list(self, request, organization_id=None):
        organization = self.get_organization()

        status_filter = request.query_params.get("status")
        source_filter = request.query_params.get("source")

        leads = get_leads_by_organization(
            organization=organization,
            status=status_filter,
            source=source_filter,
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(leads, request, view=self)
        serializer = LeadSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

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
