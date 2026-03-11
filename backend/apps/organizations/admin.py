from django.contrib import admin

from apps.organizations.models import Organization, Membership


# Register your models here.

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "organization", "role", "created_at")
    list_filter = ("role", "organization")
    search_fields = ("user__email", "organization__name")
    