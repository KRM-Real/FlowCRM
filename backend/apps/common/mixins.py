from django.shortcuts import get_object_or_404

from apps.organizations.models import Organization


class OrganizationContextMixin:
    organization_lookup_url_kwarg = "organization_id"
    organization_field_name = "organization"
    _organization = None

    def get_organization_queryset(self):
        return Organization.objects.all()

    def get_organization(self):
        if self._organization is None:
            self._organization = get_object_or_404(
                self.get_organization_queryset(),
                id=self.kwargs[self.organization_lookup_url_kwarg],
            )
        return self._organization

    def filter_organization_queryset(self, queryset):
        return queryset.filter(
            **{self.organization_field_name: self.get_organization()}
        )

    def get_organization_object(self, queryset, lookup_field="pk", lookup_url_kwarg=None):
        lookup_url_kwarg = lookup_url_kwarg or lookup_field
        return get_object_or_404(
            self.filter_organization_queryset(queryset),
            **{lookup_field: self.kwargs[lookup_url_kwarg]},
        )
