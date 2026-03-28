from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Membership

User = get_user_model()


class MembershipListSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    organization_id = serializers.IntegerField(source="organization.id", read_only=True)

    class Meta:
        model = Membership
        fields = [
            "id",
            "user_id",
            "user_email",
            "organization_id",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class MembershipCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="user",
        write_only=True,
    )

    class Meta:
        model = Membership
        fields = [
            "id",
            "user_id",
            "role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in Membership.Role.choices]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role.")
        return value

    def validate(self, attrs):
        user = attrs.get("user")
        organization = self.context.get("organization")

        if organization is None:
            raise serializers.ValidationError("Organization context is required.")

        if Membership.objects.filter(user=user, organization=organization).exists():
            raise serializers.ValidationError(
                {"user_id": "This user is already a member of this organization."}
            )

        return attrs

    def create(self, validated_data):
        organization = self.context["organization"]
        return Membership.objects.create(
            organization=organization,
            **validated_data,
        )   