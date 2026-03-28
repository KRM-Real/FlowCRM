from django.urls import path

from apps.organizations.views import OrganizationMembershipListCreateView

urlpatterns = [
    path(
        "organizations/<int:organization_id>/members/",
        OrganizationMembershipListCreateView.as_view(),
        name="organization-members",
    ),
]