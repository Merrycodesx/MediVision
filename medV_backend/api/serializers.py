from rest_framework import serializers
<<<<<<< HEAD
from .models import Hospital, Patient, Screening, ClinicalData, User


ROLE_MAP = {
    "clinician": "C",
    "radiologist": "R",
    "admin": "L",
    "auditor": "A",
}

ROLE_MAP_REVERSE = {v: k for k, v in ROLE_MAP.items()}


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    hospital_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "native_name",
            "phone_num",
            "role",
            "hospital",
            "hospital_name",
            "is_active",
            "created_at",
            "last_login",
        ]

    def get_role(self, obj):
        return ROLE_MAP_REVERSE.get(obj.role, "clinician")

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "role",
            "first_name",
            "last_name",
            "native_name",
            "phone_num",
            "hospital",
            "is_active",
        ]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "native_name": {"required": False, "allow_blank": True},
            "phone_num": {"required": False, "allow_blank": True},
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate_role(self, value):
        raw = str(value).strip().lower()
        if raw in ROLE_MAP:
            return ROLE_MAP[raw]
        if value in ROLE_MAP_REVERSE:
            return value
        raise serializers.ValidationError("Invalid role.")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        role = validated_data.pop("role", "C")
        validated_data.setdefault("native_name", "")
        validated_data.setdefault("phone_num", "")
        user = User(**validated_data)
        user.role = role
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        role = validated_data.pop("role", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if role is not None:
            instance.role = role
        if password:
            instance.set_password(password)
        instance.save()
        return instance
=======
from .models import Patient, User, ClinicalData
>>>>>>> 109c59e (some change)
=======
from .models import Patient, User, ClinicalData
>>>>>>> bf1dbb5 (some update)


class PatientSerializer(serializers.ModelSerializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=40),
        allow_empty=True
    )

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'clinician_id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        import json
        data['symptoms'] = json.loads(instance.symptoms) if instance.symptoms else []
        return data

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        import json
        internal['symptoms'] = json.dumps(internal['symptoms'])
        return internal

    def validate_age(self, value):
        if value < 0:
            raise serializers.ValidationError("Age must be a positive integer.")
        return value
    
class PatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'clinician_id']


<<<<<<< HEAD
<<<<<<< HEAD
class PatientApiSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="full_name")
    hiv_status = serializers.BooleanField(source="hiv_Status")
    sex = serializers.CharField()
    hospital_name = serializers.SerializerMethodField()
    comorbidities = serializers.ListField(
        child=serializers.CharField(max_length=40),
        allow_empty=True,
        required=False,
        write_only=True,
        default=list,
    )

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "age",
            "sex",
            "hiv_status",
            "symptoms",
            "comorbidities",
            "hospital",
            "hospital_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "hospital"]

    def validate_sex(self, value):
        raw = str(value).strip().lower()
        if raw in ("m", "male"):
            return "M"
        if raw in ("f", "female", "other"):
            return "F"
        raise serializers.ValidationError("sex must be male/female/other")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["sex"] = "male" if instance.sex == "M" else "female"
        data["comorbidities"] = []
        return data

    def get_hospital_name(self, obj):
        return obj.hospital.name if obj.hospital else None


class ScreeningSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Screening
        fields = [
            "id",
            "patient",
            "patient_name",
            "requested_by",
            "hospital",
            "tb_score",
            "triage_recommendation",
            "heatmap_url",
            "created_at",
        ]
        read_only_fields = ["id", "requested_by", "hospital", "created_at"]

    def get_patient_name(self, obj):
        return obj.patient.full_name
=======
=======
>>>>>>> bf1dbb5 (some update)
class ClinicalDataSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)
    symptoms = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    risk_factors = serializers.ListField(child=serializers.CharField(), allow_empty=True)

    class Meta:
        model = ClinicalData
        fields = ['patient_id', 'symptoms', 'risk_factors', 'age', 'sex', 'smoker', 'hiv_positive']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        import json
        data['symptoms'] = json.loads(instance.symptoms) if instance.symptoms else []
        data['risk_factors'] = json.loads(instance.risk_factors) if instance.risk_factors else []
        return data

    def to_internal_value(self, data):
        internal = super().to_internal_value(data)
        import json
        internal['symptoms'] = json.dumps(internal['symptoms'])
        internal['risk_factors'] = json.dumps(internal['risk_factors'])
        return internal

    def create(self, validated_data):
        patient_id = validated_data.pop('patient_id')
        patient = Patient.objects.get(id=patient_id)
        return ClinicalData.objects.create(patient=patient, **validated_data)
<<<<<<< HEAD
>>>>>>> 109c59e (some change)
=======
>>>>>>> bf1dbb5 (some update)


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
<<<<<<< HEAD
    hospital_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    hospital_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
=======
>>>>>>> bf1dbb5 (some update)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'password',
<<<<<<< HEAD
            'role',
            'native_name',
            'phone_num',
            'hospital',
            'hospital_code',
            'hospital_name',
=======
            'native_name',
            'phone_num',
>>>>>>> bf1dbb5 (some update)
            'first_name',
            'last_name',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
<<<<<<< HEAD
        hospital_code = (validated_data.pop('hospital_code', '') or '').strip()
        hospital_name = (validated_data.pop('hospital_name', '') or '').strip()

        hospital = validated_data.get('hospital')
        role = validated_data.get('role', 'C')

        if hospital is None and hospital_code:
            hospital = Hospital.objects.filter(code__iexact=hospital_code).first()
            if hospital is None and role == 'L':
                # Allow admin to bootstrap a new hospital by code.
                hospital = Hospital.objects.create(
                    code=hospital_code.upper(),
                    name=hospital_name or f"Hospital {hospital_code.upper()}",
                )

        if hospital is None:
            if Hospital.objects.count() == 0:
                code = (hospital_code or 'HOSP-001').upper()
                hospital = Hospital.objects.create(
                    code=code,
                    name=hospital_name or 'Default Hospital',
                )
            else:
                raise serializers.ValidationError(
                    {"hospital_code": "Provide an existing hospital_code to register in your hospital."}
                )

        validated_data['hospital'] = hospital
=======
>>>>>>> bf1dbb5 (some update)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
