from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.common.mixins import OrganizationContextMixin
from apps.organizations.models import Membership
from apps.organizations.permissions import IsOrganizationAdmin, IsOrganizationMember
from apps.organizations.serializers import (
    MembershipCreateSerializer,
    MembershipListSerializer,
    MembershipUpdateSerializer,
)


class OrganizationMembershipListCreateView(OrganizationContextMixin, ListCreateAPIView):
    queryset = Membership.objects.all()

    def get_queryset(self):
        return self.filter_organization_queryset(
            Membership.objects.select_related("user", "organization")
            .order_by("created_at", "id")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MembershipCreateSerializer
        return MembershipListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrganizationAdmin()]
        return [IsAuthenticated(), IsOrganizationMember()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def perform_create(self, serializer):
        serializer.save()


class OrganizationMembershipDetailView(OrganizationContextMixin, RetrieveUpdateDestroyAPIView):
    queryset = Membership.objects.all()
    permission_classes = [IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        return self.filter_organization_queryset(
            Membership.objects.select_related("user", "organization")
            .order_by("created_at", "id")
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
