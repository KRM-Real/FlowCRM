from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Membership
from apps.leads.models import Lead


User = get_user_model()


class LeadSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(
        source="owner",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "source",
            "status",
            "owner_id",
            "owner_email",
            "owner_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner_email",
            "owner_name",
            "created_at",
            "updated_at",
        ]

    def get_owner_name(self, obj):
        if obj.owner is None:
            return None
        full_name = f"{obj.owner.first_name} {obj.owner.last_name}".strip()
        return full_name or obj.owner.email

    def validate(self, attrs):
        value = attrs.get("owner", serializers.empty)
        if value is serializers.empty or value is None:
            return attrs

        organization = self.context.get("organization")
        if organization is None:
            raise serializers.ValidationError("Organization context is required.")

        is_member = Membership.objects.filter(
            organization=organization,
            user=value,
        ).exists()
        if not is_member:
            raise serializers.ValidationError(
                {"owner_id": "Owner must belong to this organization."}
            )

        return attrs
