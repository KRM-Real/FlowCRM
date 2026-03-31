from apps.leads.models import Lead


def get_leads_by_organization(*, organization, status=None, source=None):
    queryset = Lead.objects.filter(organization=organization)

    if status:
        queryset = queryset.filter(status=status)

    if source:
        queryset = queryset.filter(source=source)

    return queryset


def get_lead_by_id(*, lead_id, organization):
    return Lead.objects.filter(
        id=lead_id,
        organization=organization,
    ).first()
