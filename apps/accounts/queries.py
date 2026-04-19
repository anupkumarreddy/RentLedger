from django.contrib.auth import get_user_model


User = get_user_model()


def get_landlord(user_id):
    return User.objects.get(pk=user_id)
