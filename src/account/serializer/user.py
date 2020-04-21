from rest_framework.serializers import ModelSerializer
from account.models.users import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'is_staff',
            'is_active',
            'date_joined',
            'last_login'
        )
