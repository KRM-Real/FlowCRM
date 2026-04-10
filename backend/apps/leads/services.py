from apps.leads.models import Lead


def create_lead(*, organization, created_by, **data) -> Lead:
    return Lead.objects.create(
        organization=organization,
        created_by=created_by,
        **data,
    )

def update_lead(*, lead: Lead, **data) -> Lead:
    for field, value in data.items():
        setattr(lead, field, value)

    lead.save()
    return lead
