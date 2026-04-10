from django.db.models import Q

from apps.leads.models import Lead


def get_leads_by_organization(*, organization, status=None, owner=None, search=None):
    queryset = Lead.objects.filter(organization=organization)

    if status:
        queryset = queryset.filter(status=status)

    if owner:
        queryset = queryset.filter(owner_id=owner)

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(email__icontains=search)
        )

    return queryset


def get_lead_by_id(*, lead_id, organization):
    return Lead.objects.filter(
        id=lead_id,
        organization=organization,
    ).first()
