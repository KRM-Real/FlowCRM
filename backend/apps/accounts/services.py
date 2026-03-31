from django.contrib.auth import get_user_model


User = get_user_model()


def generate_unique_username(email: str) -> str:
    base_username = email.split("@", 1)[0].replace(" ", "").lower() or "user"
    candidate = base_username
    suffix = 1

    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f"{base_username}{suffix}"

    return candidate
