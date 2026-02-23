from rest_framework import serializers
from .models import Patient, User


class PatientSerializer(serializers.ModelSerializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=40),
        allow_empty=True #  Optional: Allow empty lists not needed
    )

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'clinician_id']

    def validate_age(self, value):
        if value < 0:
            raise serializers.ValidationError("Age must be a positive integer.")
        return value
    
class PatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'clinician_id']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
            'native_name',
            'phone_num',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
