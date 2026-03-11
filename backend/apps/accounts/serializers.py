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
        refresh_token = self.validated_data.get("refresh")

        if not refresh_token:
            raise serializers.ValidationError({"refresh": "Refresh token is required"})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as exc:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token"}
            ) from exc