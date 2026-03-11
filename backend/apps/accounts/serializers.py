from typing import Any, cast

from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 
                  "email", 
                  "first_name", 
                  "last_name", 
                  "is_active"
                ]

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        validated_data = cast(dict[str, Any], self.validated_data)
        refresh_token = cast(str, validated_data["refresh"])

        try:
            token = RefreshToken(refresh_token)  # type: ignore[arg-type]
            token.blacklist()
        except TokenError as exc:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token"}
            ) from exc