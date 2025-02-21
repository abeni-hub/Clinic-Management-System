# clinic/serializers.py
from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'father_name', 'grandfather_name', 'emp_id', 'gender',
            'body', 'image', 'region', 'zone', 'woreda', 'kebele', 'email', 'phone_number',
            'institution_name', 'field', 'date_of_graduate', 'company_names', 'role',
            'salary', 'pdf', 'licence_type', 'give_date', 'expired_date', 'bank_name',
            'bank_account', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        employee = Employee(**validated_data)
        employee.set_password(password)
        employee.save()
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