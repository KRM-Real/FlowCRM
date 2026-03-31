from django.contrib import admin

from apps.leads.models import Lead

# Register your models here.

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "status",
        "source",
        "organization",
        "created_by",
        "created_at"
    )
    list_filter = ("status", "source", "organization")
    search_filter = ("name", "email", "phone")
    