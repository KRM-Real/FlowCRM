from django.urls import path

from apps.leads.views import LeadViewSet


urlpatterns = [
    path(
        "",
        LeadViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="lead-list-create",
    ),
    path(
        "<uuid:pk>/",
        LeadViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="lead-detail",
    ),
]
