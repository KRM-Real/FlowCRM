import uuid

from django.conf import settings
from django.db import models

from apps.common.models import OrganizationScopedModel


class LeadStatus(models.TextChoices):
    NEW = "NEW", "New"
    CONTACTED = "CONTACTED", "Contacted"
    QUALIFIED = "QUALIFIED", "Qualified"
    LOST = "LOST", "Lost"
    WON = "WON", "Won"
    
class LeadSource(models.TextChoices):
    MANUAL = "MANUAL", "Manual"
    FACEBOOK = "FACEBOOK", "Facebook"
    WEBSITE = "WEBSITE", "Website"
    REFERRAL = "REFERRAL", "Referral"


class Lead(OrganizationScopedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)

    source = models.CharField(
        max_length=20,
        choices=LeadSource.choices,
        default=LeadSource.MANUAL,
    )

    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
    )

    class Meta:
        db_table = "leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["organization", "email"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.organization_id})"
