from django.urls import path

from apps.organizations.views import (
    OrganizationMembershipDetailView,
    OrganizationMembershipListCreateView,
)

urlpatterns = [
    path(
        "organizations/<int:organization_id>/members/",
        OrganizationMembershipListCreateView.as_view(),
        name="organization-members",
    ),
    
    path(
        "organizations/<int:organization_id>/members/<int:pk>/",
        OrganizationMembershipDetailView.as_view(),
        name="organization-member-detail",
    ),
]