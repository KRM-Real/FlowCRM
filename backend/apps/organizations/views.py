from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.organizations.models import Organization, Membership
from apps.organizations.serializers import (
    MembershipListSerializer,
    MembershipCreateSerializer,
)
from apps.organizations.permissions import (
    IsOrganizationMember,
    IsOrganizationAdmin,
)


class OrganizationMembershipListCreateView(ListCreateAPIView):
    queryset = Membership.objects.all()

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]

        return (
            Membership.objects
            .filter(organization_id=organization_id)
            .select_related("user", "organization")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MembershipCreateSerializer
        return MembershipListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated(), IsOrganizationMember()]

    def get_organization(self):
        return get_object_or_404(
            Organization,
            id=self.kwargs["organization_id"],
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def perform_create(self, serializer):
        serializer.save()