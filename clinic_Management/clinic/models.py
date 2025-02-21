# clinic/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
        return self.create_user(email, password, **extra_fields)

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

    class Meta:
        permissions = []
        default_permissions = ()

    def __str__(self):
        return f"{self.first_name} ({self.emp_id})"