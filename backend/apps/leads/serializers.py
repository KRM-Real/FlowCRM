from rest_framework import serializers

from apps.leads.models import Lead


class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "id",
            "organization",
            "created_by",
            "name",
            "email",
            "phone",
            "source",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
        ]
        