from rest_framework import serializers
from .models import Employee, Role , Patient , PatientNurseDetails , Doctor , DoctorDetails , CurrentMedication , LabResult , InjectionRoom ,Department, Appointment , Payment , LabTest , SubCategory , Category , HETSample, BodyFluidAnalysisSample, CSFAnalysisSample,PeritonealFluidAnalysisSample, SynovialFluidAnalysisSample,BacteriologySample
from .models import Department  , Tariff , Medication,MedicationPrice, Material ,CBCSample ,TWBCSample ,HGBSample ,ESRSample,BloodGroupSample,StoneExamSample,ConcentrationSample,OccultBloodSample ,PhysicalTestSample ,ChemicalTestSample,MicroscopicTestSample,HCGUrineSample,HCGSerumSample,FBSRBSSample,SGOTASTSample,SGPTALTSample,BilirubinTSample,BilirubinDSample,ALPSample,CreatinineSample,UreaSample,UricAcidSample,LipaseAmylaseSample,TotalCholesterolSample,TriglyceridesSample,LDLCSample,HDLCSample,SodiumSample,PotassiumSample, CalciumSample , WidalTestHSample , WidalTestOSample,WeilFelixTestSample,VDRLRPRTestSample,TPHATestSample ,HPyloriAntibodySample,HPyloriStoolAntigenSample,HBsAgTestSample,HCVAgTestSample,RheumatoidFactorSample, ASOTiterSample,KHBRapidTestSample,AFBTestSample, TBBloodTestSample,GramStainTestSample,WetMountTestSample,KOHPreparationSample,CultureTestSample,BFSample
from django.contrib.auth.models import Group, Permission


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
        fields = [
            'id', 'first_name', 'father_name', 'grandfather_name', 'emp_id', 'gender',
            'body', 'image', 'region', 'zone', 'woreda', 'kebele', 'email', 'phone_number',
            'institution_name', 'field', 'date_of_graduate', 'company_names', 'role',
            'salary', 'pdf', 'licence_type', 'give_date', 'expired_date', 'bank_name',
            'bank_account', 'is_active', 'password', 'department'
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

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class DoctorSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Doctor
        fields = ['id', 'employee', 'image', 'specialization', 'department']
        extra_kwargs = {'image': {'required': False}}

class CurrentMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentMedication
        fields = ['id', 'doctor_details', 'medication_type', 'dosage', 'frequency', 'prescribe_date', 'visit_date']

class LabResultSerializer(serializers.ModelSerializer):
    doctor_details = serializers.PrimaryKeyRelatedField(
        queryset=DoctorDetails.objects.all(),
        required=False,
        allow_null=True
    )
    main_category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    sub_category = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
        required=False,
        allow_null=True
    )
    uploaded_by = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        required=False,
        allow_null=True
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='sub_category.tariff.price',
        read_only=True,
        allow_null=True
    )
    
    # Use ChoiceField instead of CharField for choices
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
            ('file', 'File'),
        ],
        required=False,  # Field is optional
        allow_null=True,  # Allows `null` in input
        allow_blank=True,  # Allows empty string ("")
        default=None,    # Explicitly set default to None
    )
    result_content = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )
    class Meta:
        model = LabResult
        fields = [
            'id', 'doctor_details', 'main_category', 'sub_category',
            'result_type', 'result_content', 'result_image', 'result_file',
            'uploaded_by', 'paid', 'upload_date', 'price', 'cbc_sample'
        ]
        extra_kwargs = {
            'result_content': {'required': False, 'allow_null': True},
            'result_image': {'required': False, 'allow_null': True},
            'result_file': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        main_category = data.get('main_category')
        sub_category = data.get('sub_category')
        result_type = data.get('result_type')
        result_content = data.get('result_content')
        result_image = data.get('result_image')
        result_file = data.get('result_file')

        # Validate category relationships (unchanged)
        if main_category and sub_category:
            if sub_category.main_category != main_category:
                raise serializers.ValidationError(
                    f"The selected sub_category '{sub_category}' does not belong to the main_category '{main_category}'."
                )

        if sub_category and not sub_category.tariff:
            raise serializers.ValidationError(
                f"The selected sub_category '{sub_category}' does not have an associated tariff."
            )

        # Only validate if result_type is explicitly set (not None or blank)
        if result_type:
            if result_type == 'text' and not result_content:
                raise serializers.ValidationError(
                    {"result_content": "This field is required when result_type is 'text'."}
                )
            elif result_type == 'image' and not result_image:
                raise serializers.ValidationError(
                    {"result_image": "This field is required when result_type is 'image'."}
                )
            elif result_type == 'file' and not result_file:
                raise serializers.ValidationError(
                    {"result_file": "This field is required when result_type is 'file'."}
                )
        
        # If result_type is None/blank, no validation is enforced
        return data

from rest_framework import serializers
from .models import InjectionRoom, DoctorDetails, Employee

class InjectionRoomSerializer(serializers.ModelSerializer):
    doctor_details = serializers.PrimaryKeyRelatedField(queryset=DoctorDetails.objects.all())
    nurse = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)

    class Meta:
        model = InjectionRoom
        fields = ['id', 'doctor_details', 'medicine', 'dosage', 'dosage_price', 'frequency', 'number_of_days', 'instructions', 'date', 'nurse', 'paid', 'medication_given']

class DoctorDetailsSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)
    medications = CurrentMedicationSerializer(many=True, read_only=True)
    lab_type = serializers.CharField(required=False, allow_blank=True)
    lab_results = LabResultSerializer(many=True, read_only=True)
    injections = InjectionRoomSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorDetails
        fields = ['id', 'patient', 'visit_date', 'symptoms', 'diagnosis', 
                 'treatment_plan', 'referral_type', 'doctor', 'lab_type',
                 'medications', 'lab_results', 'injections']
        read_only_fields = ['visit_date','updated_at']

    # Remove lab_type-related code from create/update
    def create(self, validated_data):
        return DoctorDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class MedicationSerializer(serializers.ModelSerializer):
    # Use StringRelatedField or nested serializer if you want names instead of IDs
    doctor = serializers.StringRelatedField()
    
    class Meta:
        model = Medication
        fields = ['id', 'patient', 'doctor', 'name', 'dosage', 'frequency', 
                'duration', 'prescribed_at']
        read_only_fields = ['prescribed_at']  # Since it's auto_now_add

    def validate(self, data):
        # Add actual validation logic here if needed
        if data.get('duration') and not data['duration'].isdigit():
            raise serializers.ValidationError("Duration should be a number")
        return data
    
class PatientNurseDetailsSerializer(serializers.ModelSerializer):
    nurse = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)

    class Meta:
        model = PatientNurseDetails
        fields = ['id', 'patient', 'visit_date', 'pulse_rate', 'respiratory_rate', 'oxygen_saturation', 'weight', 'height', 'temperature', 'blood_pressure', 'vital_sign_attributes', 'nurse', 'updated_at']
        read_only_fields = ['visit_date', 'updated_at']

# New Serializers: AppointmentSerializer and PaymentSerializer
class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    card_no = serializers.CharField(source='patient.card_no', read_only=True)
    phone_number = serializers.CharField(source='patient.phone_number', read_only=True)
    appointed_by = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)  # Added

    class Meta:
        model = Appointment
        fields = ['id', 'patient','patient_name', 'appointment_datetime', 'appointed_by', 'reason','card_no','phone_number', 'created_at', 'status','updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            return Payment.objects.filter(patient_id=patient_id)
        return Payment.objects.all()

class PaymentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    receptionist = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)
    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    card_number = serializers.CharField(source='patient.card_no', read_only=True)
    phone_number = serializers.CharField(source='patient.phone_number', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'patient', 'patient_name', 'card_number', 'phone_number', 'payment_reason',
            'payment_amount', 'payment_type', 'receptionist', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


    def get_queryset(self):
        queryset = Payment.objects.all()
        patient_id = self.request.query_params.get('patient')  # Get 'patient' from URL
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)  # Filter by patient_id
        return queryset

class PatientSerializer(serializers.ModelSerializer):
    receptionist = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.filter(role='Receptionist'), allow_null=True)
    nurse = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.filter(role='Nurse'), allow_null=True)
    doctor = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.filter(role='Doctor'), allow_null=True)
    nurse_details = PatientNurseDetailsSerializer(many=True, read_only=True, source='nurse_visit_details')
    doctor_details = DoctorDetailsSerializer(many=True, read_only=True)  # Removed source='doctor_details'
    appointments = AppointmentSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    lab_results = LabResultSerializer(many=True, read_only=True, source='doctor_details__lab_results')
    medications = MedicationSerializer(many=True, read_only=True)  

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'grandfather_name', 'sex', 'phone_number',
            'card_no', 'kebele', 'region', 'woreda', 'registration_date','receptionist',
            'nurse', 'doctor', 'status', 'created_at', 'updated_at', 'age','medications' , 
            'nurse_details', 'doctor_details', 'appointments', 'payments', 'department','lab_results'
        ]
        read_only_fields = ['registration_date', 'updated_at', 'nurse_details', 'doctor_details', 'appointments', 'payments']

    def create(self, validated_data):
        nurse = validated_data.pop('nurse', None)
        doctor = validated_data.pop('doctor', None)

        patient = Patient.objects.create(**validated_data)

        if nurse is not None:
            patient.nurse = nurse
        if doctor is not None:
            patient.doctor = doctor

        patient.save()
        return patient

    def update(self, instance, validated_data):
        nurse = validated_data.pop('nurse', None)
        doctor = validated_data.pop('doctor', None)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.grandfather_name = validated_data.get('grandfather_name', instance.grandfather_name)
        instance.sex = validated_data.get('sex', instance.sex)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.card_no = validated_data.get('card_no', instance.card_no)
        instance.kebele = validated_data.get('kebele', instance.kebele)
        instance.region = validated_data.get('region', instance.region)
        instance.woreda = validated_data.get('woreda', instance.woreda)
        instance.receptionist = validated_data.get('receptionist', instance.receptionist)
        instance.status = validated_data.get('status', instance.status)

        if nurse is not None:
            instance.nurse = nurse
        if doctor is not None:
            instance.doctor = doctor

        instance.save()
        return instance


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'price']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']

class SubCategorySerializer(serializers.ModelSerializer):
    main_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tariff = TariffSerializer(read_only=True)
    tariff_id = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.all(), source='tariff', allow_null=True, write_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'main_category', 'tariff', 'tariff_id']

    def validate(self, data):
        tariff = data.get('tariff')
        if not tariff:
            raise serializers.ValidationError("Subcategories must have a tariff.")
        return data

class LabTestSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())

    class Meta:
        model = LabTest
        fields = ['id', 'category', 'name', 'normal_value']

class MedicationPriceSerializer(serializers.ModelSerializer):
    tariff = TariffSerializer(read_only=True)
    tariff_id = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.all(), source='tariff', allow_null=True, write_only=True)

    class Meta:
        model = MedicationPrice
        fields = ['id', 'medicine_name', 'tariff', 'tariff_id']

    def validate(self, data):
        tariff = data.get('tariff')
        if not tariff:
            raise serializers.ValidationError("Medication prices must have a tariff.")
        return data

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
class CBCSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = CBCSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        # Removed the sub_category restriction for CBC
        return data

class TWBCSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = TWBCSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        # Removed the sub_category restriction for TWBC
        # Removed the text/image validation based on lab_result.result_type
        return data

# Hematology Serializers (continued)
class ESRSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = ESRSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class BloodGroupSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BloodGroupSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class StoneExamSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = StoneExamSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class ConcentrationSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = ConcentrationSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class OccultBloodSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = OccultBloodSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

# Urinalysis Serializers
class PhysicalTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = PhysicalTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class ChemicalTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = ChemicalTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class MicroscopicTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = MicroscopicTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HCGUrineSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HCGUrineSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HCGSerumSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HCGSerumSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
class HGBSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HGBSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
# Chemistry Serializers
class FBSRBSSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = FBSRBSSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class SGOTASTSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = SGOTASTSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class SGPTALTSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = SGPTALTSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class BilirubinTSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BilirubinTSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class BilirubinDSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BilirubinDSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class ALPSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = ALPSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class CreatinineSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = CreatinineSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class UreaSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = UreaSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class UricAcidSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = UricAcidSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class LipaseAmylaseSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = LipaseAmylaseSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class TotalCholesterolSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = TotalCholesterolSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class TriglyceridesSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = TriglyceridesSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class LDLCSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = LDLCSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HDLCSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HDLCSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class SodiumSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = SodiumSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class PotassiumSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = PotassiumSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class CalciumSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = CalciumSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

# Serology Serializers
class WidalTestHSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = WidalTestHSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class WidalTestOSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = WidalTestOSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class WeilFelixTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = WeilFelixTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class VDRLRPRTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = VDRLRPRTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class TPHATestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = TPHATestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HPyloriAntibodySampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HPyloriAntibodySample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HPyloriStoolAntigenSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HPyloriStoolAntigenSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HBsAgTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HBsAgTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class HCVAgTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HCVAgTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class RheumatoidFactorSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = RheumatoidFactorSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class ASOTiterSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = ASOTiterSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class KHBRapidTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = KHBRapidTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class AFBTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = AFBTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class TBBloodSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = TBBloodTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class GramStainTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = GramStainTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
    
class WetMountTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = WetMountTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class KOHPreparationSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = KOHPreparationSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class CultureTestSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = CultureTestSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
class HETSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = HETSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class BodyFluidAnalysisSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BodyFluidAnalysisSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class CSFAnalysisSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = CSFAnalysisSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class PeritonealFluidAnalysisSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = PeritonealFluidAnalysisSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class SynovialFluidAnalysisSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = SynovialFluidAnalysisSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class BacteriologySampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BacteriologySample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data
        
class BFSampleSerializer(serializers.ModelSerializer):
    lab_result = serializers.PrimaryKeyRelatedField(queryset=LabResult.objects.all())
    result_type = serializers.ChoiceField(
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
    )

    class Meta:
        model = BFSample
        fields = '__all__'
        extra_kwargs = {
            'lab_result': {'required': False}
        }

    def validate(self, data):
        return data

class LabResultSerializer(serializers.ModelSerializer):
    doctor_details = serializers.PrimaryKeyRelatedField(queryset=DoctorDetails.objects.all())
    main_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True)
    sub_category = SubCategorySerializer(read_only=True)
    uploaded_by = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), allow_null=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='sub_category.tariff.price', read_only=True, allow_null=True)
    
    # Sample fields (PrimaryKeyRelatedField for all)
    cbc_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    twbc_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hgb_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    esr_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    blood_group_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    stone_exam_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    concentration_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    occult_blood_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    physical_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    chemical_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    microscopic_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hcg_urine_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hcg_serum_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    fbs_rbs_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    sgot_ast_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    sgpt_alt_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    bilirubin_t_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    bilirubin_d_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    alp_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    creatinine_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    urea_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    uric_acid_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    lipase_amylase_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    total_cholesterol_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    triglycerides_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    ldlc_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hdlc_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    sodium_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    potassium_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    calcium_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    widal_test_h_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    widal_test_o_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    weil_felix_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    vdrl_rpr_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    tpha_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    h_pylori_antibody_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    h_pylori_stool_antigen_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hbsag_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    hcvag_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    rheumatoid_factor_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    aso_titer_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    khb_rapid_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    afb_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    tb_blood_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    gram_stain_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    wet_mount_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    koh_preparation_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    culture_test_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    het_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    body_fluid_analysis_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    csf_analysis_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    peritoneal_fluid_analysis_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    synovial_fluid_analysis_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    bacteriology_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    bf_sample = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)

    sub_category_id = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.all(),
        source='sub_category',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = LabResult
        fields = [
            'id', 'doctor_details', 'main_category', 'sub_category', 'sub_category_id',
            'result_type', 'result_content', 'result_image', 'result_file', 
            'uploaded_by', 'paid', 'upload_date', 'price',
            # Sample fields
            'cbc_sample', 'twbc_sample', 'hgb_sample', 'esr_sample',
            'blood_group_sample', 'stone_exam_sample', 'concentration_sample',
            'occult_blood_sample', 'physical_test_sample', 'chemical_test_sample',
            'microscopic_test_sample', 'hcg_urine_sample', 'hcg_serum_sample',
            'fbs_rbs_sample', 'sgot_ast_sample', 'sgpt_alt_sample',
            'bilirubin_t_sample', 'bilirubin_d_sample', 'alp_sample',
            'creatinine_sample', 'urea_sample', 'uric_acid_sample',
            'lipase_amylase_sample', 'total_cholesterol_sample',
            'triglycerides_sample', 'ldlc_sample', 'hdlc_sample',
            'sodium_sample', 'potassium_sample', 'calcium_sample',
            'widal_test_h_sample', 'widal_test_o_sample',
            'weil_felix_test_sample', 'vdrl_rpr_test_sample',
            'tpha_test_sample', 'h_pylori_antibody_sample',
            'h_pylori_stool_antigen_sample', 'hbsag_test_sample',
            'hcvag_test_sample', 'rheumatoid_factor_sample',
            'aso_titer_sample', 'khb_rapid_test_sample',
            'afb_test_sample', 'tb_blood_test_sample',
            'gram_stain_test_sample', 'wet_mount_test_sample',
            'koh_preparation_sample', 'culture_test_sample',
            'het_sample', 'body_fluid_analysis_sample', 'csf_analysis_sample',
            'peritoneal_fluid_analysis_sample', 'synovial_fluid_analysis_sample',
            'bacteriology_sample','bf_sample'
        ]

    def validate(self, data):
        main_category = data.get('main_category')
        sub_category = data.get('sub_category')
        result_type = data.get('result_type')
        result_content = data.get('result_content')

        if main_category and sub_category:
            if sub_category.main_category != main_category:
                raise serializers.ValidationError(
                    f"The selected sub_category '{sub_category}' does not belong to the main_category '{main_category}'."
                )

        if sub_category and not sub_category.tariff:
            raise serializers.ValidationError(
                f"The selected sub_category '{sub_category}' does not have an associated tariff."
            )

        if result_type == 'text' and not result_content:
            raise serializers.ValidationError("result_content cannot be empty when result_type is 'text'.")

        return data

    def to_internal_value(self, data):
        if 'sub_category' in data:
            sub_category_id = data.get('sub_category')
            try:
                data['sub_category'] = SubCategory.objects.get(id=sub_category_id)
            except SubCategory.DoesNotExist:
                raise serializers.ValidationError("Invalid sub_category ID.")
        return super().to_internal_value(data)
