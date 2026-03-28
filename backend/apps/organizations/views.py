from django.shortcuts import get_object_or_404

from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.organizations.models import Organization, Membership
from apps.organizations.permissions import IsOrganizationAdmin, IsOrganizationMember
from apps.organizations.serializers import (
    MembershipCreateSerializer,
    MembershipListSerializer,
    MembershipUpdateSerializer,
)


class OrganizationMembershipListCreateView(ListCreateAPIView):
    queryset = Membership.objects.all()

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        return (
            Membership.objects.filter(organization_id=organization_id)
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


class OrganizationMembershipDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Membership.objects.all()
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        organization_id = self.kwargs["organization_id"]
        return (
            Membership.objects.filter(organization_id=organization_id)
            .select_related("user", "organization")
        )

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return MembershipUpdateSerializer
        return MembershipListSerializer

    def perform_destroy(self, instance):
        if instance.role == Membership.Role.ADMIN:
            admin_count = Membership.objects.filter(
                organization=instance.organization,
                role=Membership.Role.ADMIN,
            ).count()

            if admin_count <= 1:
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    {"detail": "You cannot remove the last admin from the organization."}
                )

        instance.delete()