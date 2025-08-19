from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Employee(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to='employee_images/', blank=True, null=True)
    region = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    woreda = models.CharField(max_length=100)
    kebele = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    institution_name = models.CharField(max_length=200)
    field = models.CharField(max_length=100)
    date_of_graduate = models.DateField()
    company_names = models.CharField(max_length=200)
    role = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees")


    salary = models.DecimalField(max_digits=10, decimal_places=2)
    pdf = models.FileField(upload_to='employee_docs/', blank=True, null=True)
    licence_type = models.CharField(max_length=100)
    give_date = models.DateField()
    expired_date = models.DateField()
    bank_name = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=50)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'emp_id', 'password']

    def str(self):
        return f"{self.first_name} ({self.emp_id})"
    
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def str(self):
        return self.name
    
    ### update for patients =======================================


class Patient(models.Model):
    # STATUS_CHOICES = (
    #     ('Registered', 'Registered'),
    #     ('Vital Sign Added', 'Vital Sign Added'),
    #     ('Seen By Doctor', 'Seen by Doctor'),
    #     ('Lab Reviewed', 'Lab Reviewed'),  # Updated key and display value
    #     ('Injection Room', 'Injection Room'),
    #     ('Completed', 'Completed'),
    # )
 
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    phone_number = models.CharField(max_length=20)
    card_no = models.CharField(max_length=50)
    kebele = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    woreda = models.CharField(max_length=100)
    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50)  # Removed default value
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='registered_patients')
    nurse = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='nurse_patients', blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="patients")

    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='doctor_patients', blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    age = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.id})"

    class Meta:
        ordering = ['-registration_date']
class PatientNurseDetails(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='nurse_visit_details')
    visit_date = models.DateTimeField(auto_now_add=True)
    pulse_rate = models.PositiveIntegerField(blank=True, null=True)
    respiratory_rate = models.PositiveIntegerField(blank=True, null=True)
    oxygen_saturation = models.PositiveIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    vital_sign_attributes = models.TextField(blank=True, null=True)
    nurse = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='nurse_patient_visit_details')
    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='doctor_patient_visit_details', limit_choices_to={'role': 'Doctor'})
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Nurse Visit Details for {self.patient} on {self.visit_date}"

class Doctor(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='doctor_profile')
    image = models.ImageField(upload_to='doctor_images/', blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')

    def __str__(self):
        return f"Dr. {self.employee.first_name} {self.employee.last_name}"

    class Meta:
        ordering = ['employee__first_name']
class DoctorDetails(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctor_details')
    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Doctor'})
    visit_date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField(blank=True)  # This field exists in the model
    lab_type = models.CharField(max_length=100, blank=True, null=True)  # or whatever field type you need

    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    referral_type = models.CharField(
    max_length=20,
    choices=[
        ('lab_only', 'Lab Only'),
        ('injection_only', 'Injection Only'),
        ('both', 'Both'),
        ('none', 'None'),
    ],
    default='none',
    blank=True,  # Allows empty string in forms
    null=True,   # Allows NULL in database (optional)
)
    def __str__(self):
        return f"Doctor Details for {self.patient} by {self.doctor}"

    class Meta:
        ordering = ['-visit_date']

class CurrentMedication(models.Model):
    doctor_details = models.ForeignKey('DoctorDetails', on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} for {self.doctor_details}"

class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')    
    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='prescribed_medications', limit_choices_to={'role': 'Doctor'})
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    prescribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} for {self.patient} by {self.doctor}"

    class Meta:
        ordering = ['-prescribed_at']

class Tariff(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}: {self.price}"

    class Meta:
        verbose_name_plural = "Tariffs"
        ordering = ['name']
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class SubCategory(models.Model):
    name = models.CharField(max_length=255)
    main_category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

    class Meta:
        verbose_name_plural = "SubCategories"
        ordering = ['main_category', 'name']

class LabTest(models.Model):
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=100)
    normal_value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.category} - {self.name}"

    class Meta:
        ordering = ['category', 'name']

class LabResult(models.Model):
    doctor_details = models.ForeignKey(DoctorDetails, on_delete=models.CASCADE, related_name='lab_results', null=True, blank=True)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lab_results', null=True, blank=True)

    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='lab_results', null=True, blank=True)
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
            ('file', 'File'),
        ],
        null=True,      # Allows NULL in database
        blank=True,     # Allows blank in forms
        default=None,   # Explicitly set default to None
    )
    result_content = models.TextField(blank=True, null=True, default=None)
    result_image = models.ImageField(upload_to='lab_results/images/', blank=True, null=True)
    result_file = models.FileField(upload_to='lab_results/files/', blank=True, null=True)
    uploaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    paid = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"Lab Result for {self.doctor_details} - {self.main_category} - {self.sub_category}"

    class Meta: 
        ordering = ['-upload_date']

from django.db import models
from django.contrib.auth import get_user_model

class InjectionRoom(models.Model):
    FREQUENCY_CHOICES = (
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('as_needed', 'As Needed'),
    )

    doctor_details = models.ForeignKey('DoctorDetails', on_delete=models.CASCADE, related_name='injections')
    nurse = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='injection_results_uploaded')
    medicine = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    dosage_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    frequency = models.CharField(max_length=50)
    number_of_days = models.PositiveIntegerField()
    instructions = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    medication_given = models.BooleanField(default=False)
    paid = models.BooleanField(default=False, verbose_name="Payment Status")

    def __str__(self):
        return f"Injection for {self.doctor_details.patient} on {self.date}"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    appointment_datetime = models.DateTimeField()
    appointed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='scheduled_appointments')  # Added
    reason = models.TextField(blank=True)  # Added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='scheduled')  # Normal text field

    def __str__(self):
        return f"Appointment for {self.patient} on {self.appointment_datetime}"

    class Meta:
        ordering = ['-appointment_datetime']

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('Cash', 'Cash'),
        ('Transfer', 'Transfer'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    payment_reason = models.CharField(max_length=200)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='verified_payments', blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment of {self.payment_amount} for {self.patient} ({self.payment_reason})"

    class Meta:
        ordering = ['-created_at']




# Hematology Models
class CBCSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='cbc_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    wbc = models.FloatField(null=True, blank=True)
    lymph_percent = models.FloatField(null=True, blank=True)
    lymph_absolute = models.FloatField(null=True, blank=True)
    gran_percent = models.FloatField(null=True, blank=True)
    gran_absolute = models.FloatField(null=True, blank=True)
    mid_percent = models.FloatField(null=True, blank=True)
    mid_absolute = models.FloatField(null=True, blank=True)
    rbc = models.FloatField(null=True, blank=True)
    hgb = models.FloatField(null=True, blank=True)
    hct = models.FloatField(null=True, blank=True)
    mcv = models.FloatField(null=True, blank=True)
    mch = models.FloatField(null=True, blank=True)
    mchc = models.FloatField(null=True, blank=True)
    rdw_cv = models.FloatField(null=True, blank=True)
    rdw_sd = models.FloatField(null=True, blank=True)
    plt = models.FloatField(null=True, blank=True)
    mpv = models.FloatField(null=True, blank=True)
    pdw = models.FloatField(null=True, blank=True)
    pct = models.FloatField(null=True, blank=True)
    p_lcr = models.FloatField(null=True, blank=True)
    p_lcc = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='cbc_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"CBC Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class TWBCSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='twbc_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    wbc = models.FloatField(null=True, blank=True)
    lymph_percent = models.FloatField(null=True, blank=True)
    lymph_absolute = models.FloatField(null=True, blank=True)
    gran_percent = models.FloatField(null=True, blank=True)
    gran_absolute = models.FloatField(null=True, blank=True)
    mid_percent = models.FloatField(null=True, blank=True)
    mid_absolute = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='twbc_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"TWBC Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HGBSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hgb_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    hgb = models.FloatField(null=True, blank=True)
    rbc = models.FloatField(null=True, blank=True)
    hct = models.FloatField(null=True, blank=True)
    mcv = models.FloatField(null=True, blank=True)
    mch = models.FloatField(null=True, blank=True)
    mchc = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hgb_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HGB Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class ESRSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='esr_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    esr = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='esr_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"ESR Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class BloodGroupSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='blood_group_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    rh_factor = models.CharField(max_length=10, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='blood_group_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Blood Group Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HETSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='het_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    het = models.FloatField(null=True, blank=True)
    hgb = models.FloatField(null=True, blank=True)
    rbc = models.FloatField(null=True, blank=True)
    mcv = models.FloatField(null=True, blank=True)
    mch = models.FloatField(null=True, blank=True)
    mchc = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='het_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HET Sample {self.sampleid} for Lab Result {self.lab_result_id}"

# Urinalysis Models
class StoneExamSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='stone_exam_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    stone_type = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    consistency = models.CharField(max_length=100, null=True, blank=True)
    microscopic_examination = models.TextField(blank=True, null=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='stone_exam_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Stone Exam Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class ConcentrationSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='concentration_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    reaction_ph = models.FloatField(null=True, blank=True)
    specific_gravity = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='concentration_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Concentration Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class OccultBloodSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='occult_blood_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    occult_blood_result = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='occult_blood_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Occult Blood Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class PhysicalTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='physical_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    reaction_ph = models.FloatField(null=True, blank=True)
    specific_gravity = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='physical_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Physical Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class ChemicalTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='chemical_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    protein = models.CharField(max_length=100, null=True, blank=True)
    glucose = models.CharField(max_length=100, null=True, blank=True)
    ketone = models.CharField(max_length=100, null=True, blank=True)
    bilirubin = models.CharField(max_length=100, null=True, blank=True)
    urobilinogen = models.CharField(max_length=100, null=True, blank=True)
    blood = models.CharField(max_length=100, null=True, blank=True)
    nitrite = models.CharField(max_length=100, null=True, blank=True)
    leukocyte_esterase = models.CharField(max_length=100, null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    specific_gravity = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chemical_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Chemical Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class MicroscopicTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='microscopic_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    rbcs = models.CharField(max_length=100, null=True, blank=True)
    wbcs = models.CharField(max_length=100, null=True, blank=True)
    epithelial_cells = models.CharField(max_length=100, null=True, blank=True)
    casts = models.CharField(max_length=100, null=True, blank=True)
    crystals = models.CharField(max_length=100, null=True, blank=True)
    bacteria = models.CharField(max_length=100, null=True, blank=True)
    yeast = models.CharField(max_length=100, null=True, blank=True)
    parasites = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='microscopic_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Microscopic Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HCGUrineSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hcg_urine_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    hcg_result = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hcg_urine_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HCG Urine Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HCGSerumSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hcg_serum_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    hcg_level = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hcg_serum_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HCG Serum Sample {self.sampleid} for Lab Result {self.lab_result_id}"

# Chemistry Models
class FBSRBSSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='fbs_rbs_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    test_type = models.CharField(max_length=10, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='fbs_rbs_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"FBS/RBS Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class SGOTASTSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='sgot_ast_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sgot_ast_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"SGOT/AST Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class SGPTALTSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='sgpt_alt_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sgpt_alt_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"SGPT/ALT Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class BilirubinTSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='bilirubin_t_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='bilirubin_t_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Bilirubin (Total) Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class BilirubinDSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='bilirubin_d_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='bilirubin_d_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Bilirubin (Direct) Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class ALPSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='alp_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='alp_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"ALP Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class CreatinineSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='creatinine_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='creatinine_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Creatinine Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class UreaSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='urea_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='urea_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Urea Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class UricAcidSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='uric_acid_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='uric_acid_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Uric Acid Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class LipaseAmylaseSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='lipase_amylase_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    lipase_result = models.FloatField(null=True, blank=True)
    lipase_reference = models.CharField(max_length=100, null=True, blank=True)
    amylase_result = models.FloatField(null=True, blank=True)
    amylase_reference = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='lipase_amylase_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Lipase/Amylase Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class TotalCholesterolSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='total_cholesterol_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='total_cholesterol_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Total Cholesterol Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class TriglyceridesSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='triglycerides_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='triglycerides_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Triglycerides Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class LDLCSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='ldlc_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='ldlc_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"LDL-C Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HDLCSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hdlc_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hdlc_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HDL-C Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class SodiumSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='sodium_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='sodium_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Sodium Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class PotassiumSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='potassium_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='potassium_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Potassium Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class CalciumSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='calcium_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    result = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='calcium_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Calcium Sample {self.sampleid} for Lab Result {self.lab_result_id}"

# Serology Models
class WidalTestHSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='widal_test_h_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    widal_h_antigen_titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='widal_test_h_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Widal Test H Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class WidalTestOSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='widal_test_o_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    widal_o_antigen_titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='widal_test_o_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Widal Test O Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class WeilFelixTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='weil_felix_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    antigen_ox19_titer = models.CharField(max_length=100, null=True, blank=True)
    antigen_ox2_titer = models.CharField(max_length=100, null=True, blank=True)
    antigen_oxk_titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='weil_felix_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Weil Felix Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class VDRLRPRTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='vdrl_rpr_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    test_result = models.CharField(max_length=100, null=True, blank=True)
    titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='vdrl_rpr_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"VDRL/RPR Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class TPHATestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='tpha_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    tpha_result = models.CharField(max_length=100, null=True, blank=True)
    titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='tpha_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"TPHA Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HPyloriAntibodySample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='h_pylori_antibody_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    antibody_result = models.CharField(max_length=100, null=True, blank=True)
    titer = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='h_pylori_antibody_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"H. Pylori Antibody Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HPyloriStoolAntigenSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='h_pylori_stool_antigen_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    stool_antigen_result = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='h_pylori_stool_antigen_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"H. Pylori Stool Antigen Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HBsAgTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hbsag_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    hbsag_result = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hbsag_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HBsAg Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class HCVAgTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='hcv_ag_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    hcvag_result = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='hcvag_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"HCVAg Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class RheumatoidFactorSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='rheumatoid_factor_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    rf_result = models.CharField(max_length=100, null=True, blank=True)
    rf_value = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='rheumatoid_factor_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Rheumatoid Factor Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class ASOTiterSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='aso_titer_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    aso_titer = models.FloatField(null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='aso_titer_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"ASO Titer Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class KHBRapidTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='khb_rapid_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    rapid_test_result = models.CharField(max_length=100, null=True, blank=True)
    test_type = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='khb_rapid_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"KHB Rapid Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

# Bacteriology Models
class AFBTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='afb_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    spot_sample_result = models.CharField(max_length=100, null=True, blank=True)
    morning_sample_result = models.CharField(max_length=100, null=True, blank=True)
    second_spot_sample_result = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='afb_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"AFB Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class TBBloodTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='tb_blood_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    tb_blood_test_result = models.CharField(max_length=100, null=True, blank=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    reference_range = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='tb_blood_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"TB Blood Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class GramStainTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='gram_stain_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=True)
    organism_type = models.CharField(max_length=100, null=True, blank=True)
    cellular_elements = models.TextField(blank=True, null=True)
    background = models.TextField(blank=True, null=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='gram_stain_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Gram Stain Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class WetMountTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='wet_mount_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=True)
    organisms_observed = models.TextField(blank=True, null=True)
    motility = models.CharField(max_length=100, null=True, blank=True)
    pus_cells = models.CharField(max_length=100, null=True, blank=True)
    rbcs = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='wet_mount_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Wet Mount Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class KOHPreparationSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='koh_preparation_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=True)
    fungal_elements = models.TextField(blank=True, null=True)
    yeast_cells = models.CharField(max_length=100, null=True, blank=True)
    pseudohyphae = models.CharField(max_length=100, null=True, blank=True)
    background = models.TextField(blank=True, null=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='koh_preparation_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"KOH Preparation Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class CultureTestSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='culture_test_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=True)
    organism_isolated = models.CharField(max_length=100, null=True, blank=True)
    growth_description = models.TextField(blank=True, null=True)
    antibiotic_sensitivity = models.TextField(blank=True, null=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='culture_test_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Culture Test Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class BacteriologySample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='bacteriology_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    sample_type = models.CharField(max_length=100, null=True, blank=True)
    culture_result = models.CharField(max_length=100, null=True, blank=True)
    colony_count = models.CharField(max_length=100, null=True, blank=True)
    antibiotic_sensitivity_pattern = models.TextField(blank=True, null=True)
    method_used = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='bacteriology_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Bacteriology Sample {self.sampleid} for Lab Result {self.lab_result_id}"

# Fluid Analysis Models
class BodyFluidAnalysisSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='body_fluid_analysis_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    fluid_type = models.CharField(max_length=100, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    rbc_count = models.FloatField(null=True, blank=True)
    wbc_count = models.FloatField(null=True, blank=True)
    neutrophils = models.FloatField(null=True, blank=True)
    lymphocytes = models.FloatField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='body_fluid_analysis_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Body Fluid Analysis Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class CSFAnalysisSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='csf_analysis_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    rbc_count = models.FloatField(null=True, blank=True)
    wbc_count = models.FloatField(null=True, blank=True)
    neutrophils = models.FloatField(null=True, blank=True)
    lymphocytes = models.FloatField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    chloride = models.FloatField(null=True, blank=True)
    opening_pressure = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='csf_analysis_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"CSF Analysis Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class PeritonealFluidAnalysisSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='peritoneal_fluid_analysis_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    rbc_count = models.FloatField(null=True, blank=True)
    wbc_count = models.FloatField(null=True, blank=True)
    neutrophils = models.FloatField(null=True, blank=True)
    lymphocytes = models.FloatField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    ldh = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='peritoneal_fluid_analysis_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Peritoneal Fluid Analysis Sample {self.sampleid} for Lab Result {self.lab_result_id}"

class SynovialFluidAnalysisSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='synovial_fluid_analysis_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=100, null=True, blank=True)
    appearance = models.CharField(max_length=100, null=True, blank=True)
    viscosity = models.CharField(max_length=100, null=True, blank=True)
    rbc_count = models.FloatField(null=True, blank=True)
    wbc_count = models.FloatField(null=True, blank=True)
    neutrophils = models.FloatField(null=True, blank=True)
    lymphocytes = models.FloatField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    crystals = models.CharField(max_length=100, null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='synovial_fluid_analysis_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"Synovial Fluid Analysis Sample {self.sampleid} for Lab Result {self.lab_result_id}"
        
class BFSample(models.Model):
    lab_result = models.OneToOneField('LabResult', on_delete=models.CASCADE, related_name='bf_sample')
    result_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
        ],
        null=True,
        blank=True,
        default=None,
    )
    sampleid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    parasite_seen = models.CharField(
        max_length=3,
        choices=[
            ('Yes', 'Yes'),
            ('No', 'No'),
        ],
        null=True,
        blank=True,
    )
    parasite_species = models.CharField(max_length=100, null=True, blank=True)
    parasite_stage = models.CharField(max_length=100, null=True, blank=True)
    parasite_density = models.FloatField(null=True, blank=True)
    additional_note = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='bf_sample/images/', blank=True, null=True)

    def __str__(self):
        return f"BF Sample {self.sampleid} for Lab Result {self.lab_result_id}"


class MedicationPrice(models.Model):
    medicine_name = models.CharField(max_length=255)
    tariff = models.ForeignKey('Tariff', on_delete=models.SET_NULL, null=True, blank=True, related_name='medication_prices')

    def __str__(self):
        return self.medicine_name

    class Meta:
        verbose_name_plural = "MedicationPrices"
        ordering = ['medicine_name']

class Material(models.Model):
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=100)
    quantity = models.IntegerField()
    assigned_person = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.assigned_person}"

    class Meta:
        verbose_name_plural = "Materials"
        ordering = ['name']
