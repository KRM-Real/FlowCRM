from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel

# Create your models here.

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    def __str__(self) -> str:
        return self.name
    
    
class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        REP = "rep", "Rep"
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete= models.CASCADE,
        related_name= "memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete= models.CASCADE,
        related_name= "memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    
    class Meta:
        unique_together = ("user", "organization")
        
    def __str__(self) -> str:
        return f"{self.user.email} - {self.organization.name} ({self.role})"