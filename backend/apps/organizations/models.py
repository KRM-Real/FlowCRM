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
    role = models.CharField(
        max_length=20, 
        choices=Role.choices,
        default=Role.REP)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership"
            )
        ]
        indexes = [
            models.Index(fields=["organization", "role"]),
            models.Index(fields=["user", "role"]),
        ]
        
    def __str__(self) -> str:
        return f"{self.user.email} - {self.organization.name} ({self.role})"
    
    
    @property
    def is_manager(self) -> bool:
        return self.role == self.Role.MANAGER
    
    @property
    def is_rep(self) -> bool:
        return self.role == self.Role.REP
    
    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager_or_admin(self) -> bool:
        return self.role in {self.Role.ADMIN, self.Role.MANAGER}