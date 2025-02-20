# clinic/serializers.py
from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import Group, Permission

class EmployeeSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )
    user_permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'father_name', 'grandfather_name', 'emp_id', 'gender',
            'body', 'image', 'region', 'zone', 'woreda', 'kebele', 'email', 'phone_number',
            'institution_name', 'field', 'date_of_graduate', 'company_names', 'role',
            'salary', 'pdf', 'licence_type', 'give_date', 'expired_date', 'bank_name',
            'bank_account', 'groups', 'user_permissions', 'is_active', 'is_staff', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', [])
        user_permissions_data = validated_data.pop('user_permissions', [])
        password = validated_data.pop('password')
        
        employee = Employee(**validated_data)
        employee.set_password(password)
        employee.save()
        
        if groups_data:
            employee.groups.set(groups_data)
        if user_permissions_data:
            employee.user_permissions.set(user_permissions_data)
        
        return employee

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    def validate(self, attrs):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken(attrs['refresh'])
        data = {'access': str(refresh.access_token)}
        if refresh.payload.get('rotating_refresh_token', False):
            data['refresh'] = str(refresh)
        return data