from rest_framework.permissions import BasePermission

from apps.organizations.models import Organization
from apps.organizations.services import (
    is_organization_admin,
    is_organization_manager_or_admin,
    user_belongs_to_organization,
)


class BaseOrganizationPermission(BasePermission):
    message = "You do not have permission to access this organization."

    def get_organization(self, view):
        organization_id = view.kwargs.get("organization_id")
        if not organization_id:
            return None

        try:
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return None


class IsOrganizationMember(BaseOrganizationPermission):
    message = "You must be a member of this organization."

    def has_permission(self, request, view) -> bool:
        organization = self.get_organization(view)
        if organization is None:
            return False

        return user_belongs_to_organization(request.user, organization)


class IsOrganizationAdmin(BaseOrganizationPermission):
    message = "You must be an admin of this organization."

    def has_permission(self, request, view) -> bool:
        organization = self.get_organization(view)
        if organization is None:
            return False

        return is_organization_admin(request.user, organization)


class IsOrganizationManagerOrAdmin(BaseOrganizationPermission):
    message = "You must be a manager or admin of this organization."

    def has_permission(self, request, view) -> bool:
        organization = self.get_organization(view)
        if organization is None:
            return False

        return is_organization_manager_or_admin(request.user, organization)