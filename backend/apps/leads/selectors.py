from apps.leads.models import Lead


def get_leads_by_organization(*, organization):
    return Lead.objects.filter(organization=organization)


def get_lead_by_id(*, lead_id, organization):
    return Lead.objects.filter(
        id=lead_id,
        organization=organization,
    ).first()