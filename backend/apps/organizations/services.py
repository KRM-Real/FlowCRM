from typing import Optional

from django.contrib.auth import get_user_model

from apps.organizations.models import Membership, Organization

User = get_user_model()


def get_user_membership(user, organization: Organization) -> Optional[Membership]:
    if not user or not user.is_authenticated:
        return None

    return (
        Membership.objects.select_related("organization", "user")
        .filter(user=user, organization=organization)
        .first()
    )


def user_belongs_to_organization(user, organization: Organization) -> bool:
    return get_user_membership(user, organization) is not None


def is_organization_admin(user, organization: Organization) -> bool:
    membership = get_user_membership(user, organization)
    return membership is not None and membership.is_admin


def is_organization_manager_or_admin(user, organization: Organization) -> bool:
    membership = get_user_membership(user, organization)
    return membership is not None and membership.is_manager_or_admin