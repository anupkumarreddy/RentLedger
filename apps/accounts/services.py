from django.contrib.auth import get_user_model


User = get_user_model()


def create_landlord_account(*, email, password, full_name, phone=""):
    return User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
    )
