from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    EmployeeSerializer, LoginSerializer, TokenRefreshSerializer, RoleSerializer, PatientSerializer,
    PatientNurseDetailsSerializer, DoctorSerializer, DoctorDetailsSerializer, LabResultSerializer,
    InjectionRoomSerializer, DepartmentSerializer, AppointmentSerializer, PaymentSerializer,
    CategorySerializer, SubCategorySerializer, LabTestSerializer, TariffSerializer, MedicationSerializer , CBCSampleSerializer , TWBCSampleSerializer, HGBSampleSerializer ,ESRSampleSerializer, BloodGroupSampleSerializer, StoneExamSampleSerializer, ConcentrationSampleSerializer, OccultBloodSampleSerializer, PhysicalTestSampleSerializer, ChemicalTestSampleSerializer, MicroscopicTestSampleSerializer, HCGUrineSampleSerializer, HCGSerumSampleSerializer, FBSRBSSampleSerializer, SGOTASTSampleSerializer, SGPTALTSampleSerializer, BilirubinTSampleSerializer, BilirubinDSampleSerializer, ALPSampleSerializer, CreatinineSampleSerializer, UreaSampleSerializer, UricAcidSampleSerializer, LipaseAmylaseSampleSerializer, TotalCholesterolSampleSerializer, TriglyceridesSampleSerializer, LDLCSampleSerializer, HDLCSampleSerializer, SodiumSampleSerializer, PotassiumSampleSerializer , KHBRapidTestSampleSerializer , AFBTestSampleSerializer,
    CalciumSampleSerializer, WidalTestHSampleSerializer, WidalTestOSampleSerializer, WeilFelixTestSampleSerializer, VDRLRPRTestSampleSerializer, TPHATestSampleSerializer, HPyloriAntibodySampleSerializer, HPyloriStoolAntigenSampleSerializer, HBsAgTestSampleSerializer, HCVAgTestSampleSerializer, RheumatoidFactorSampleSerializer, ASOTiterSampleSerializer, TBBloodSampleSerializer , GramStainTestSampleSerializer , WetMountTestSampleSerializer, KOHPreparationSampleSerializer, CultureTestSampleSerializer,
    HETSampleSerializer, BodyFluidAnalysisSampleSerializer,
    CSFAnalysisSampleSerializer, PeritonealFluidAnalysisSampleSerializer,
    SynovialFluidAnalysisSampleSerializer, BacteriologySampleSerializer ,MedicationPriceSerializer, MaterialSerializer,BFSampleSerializer
)
from django.db.models import Prefetch
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from .models import (
    Employee, Patient, Role, PatientNurseDetails, Doctor, DoctorDetails, CurrentMedication,
    Medication, LabResult, InjectionRoom, Department, Appointment, Payment, Category, SubCategory, LabTest, Tariff ,
    HETSample, BodyFluidAnalysisSample,
    CSFAnalysisSample, PeritonealFluidAnalysisSample, SynovialFluidAnalysisSample,
    BacteriologySample ,MedicationPrice, Material 
    )
from .models import Department  , Tariff , Medication ,CBCSample ,TWBCSample ,HGBSample ,ESRSample,BloodGroupSample,StoneExamSample,ConcentrationSample,OccultBloodSample ,PhysicalTestSample ,ChemicalTestSample,MicroscopicTestSample,HCGUrineSample,HCGSerumSample,FBSRBSSample,SGOTASTSample,SGPTALTSample,BilirubinTSample,BilirubinDSample,ALPSample,CreatinineSample,UreaSample,UricAcidSample,LipaseAmylaseSample,TotalCholesterolSample,TriglyceridesSample,LDLCSample,HDLCSample,SodiumSample,PotassiumSample, CalciumSample , WidalTestHSample , WidalTestOSample,WeilFelixTestSample,VDRLRPRTestSample,TPHATestSample ,HPyloriAntibodySample,HPyloriStoolAntigenSample,HBsAgTestSample,HCVAgTestSample,RheumatoidFactorSample, ASOTiterSample,KHBRapidTestSample,AFBTestSample, TBBloodTestSample,GramStainTestSample,WetMountTestSample,KOHPreparationSample,CultureTestSample,BFSample
from django.http import Http404 
from rest_framework import views, viewsets , filters
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect , render
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        queryset = queryset.select_related('department')
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmployeeRegistrationView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        refresh = RefreshToken.for_user(employee)
        return Response({
            'employee': EmployeeSerializer(employee).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            employee = Employee.objects.get(email=email)
            if employee.check_password(password):
                refresh = RefreshToken.for_user(employee)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'employee': EmployeeSerializer(employee).data
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Employee.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(generics.GenericAPIView):
    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            employee = Employee.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(employee.pk))
            token = default_token_generator.make_token(employee)
            reset_link = f"http://127.0.0.1:8000/api/reset/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=True,
            )
            return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            employee = Employee.objects.get(pk=uid)
            if default_token_generator.check_token(employee, token):
                new_password = request.data.get('new_password')
                if not new_password:
                    return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
                employee.set_password(new_password)
                employee.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, Employee.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

def create_patient(request):
    if request.method == 'POST':
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) if department_id else None
        patient = Patient.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            department=department,
        )
        return redirect('patient_list')
    return render(request, 'create_patient.html', {'departments': Department.objects.all()})

class EmployeeListView(ListAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        email = self.request.GET.get('email')
        queryset = Employee.objects.all()
        if email:
            return queryset.filter(email=email)
        return queryset

class EmployeeDetailView(generics.RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'id'

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

@api_view(['POST'])
def logout_view(request):
    response = Response({"message": "Logged out successfully"}, status=200)
    response.delete_cookie("jwt")
    return response
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['receptionist', 'nurse', 'doctor', 'department']  
    search_fields = ['first_name', 'last_name', 'phone_number']  
    ordering_fields = ['created_at', 'updated_at']  
    ordering = ['-created_at'] 

    def get_queryset(self):
        queryset = super().get_queryset()
        # Your existing filtering logic...
        
        # Optimize queries for patient details
        queryset = queryset.select_related(
            'receptionist', 'nurse', 'doctor', 'department'
        ).prefetch_related(
            'nurse_visit_details',
            Prefetch(
                'doctor_details__lab_results',
                queryset=LabResult.objects.select_related(
                    'main_category',
                    'sub_category',
                    'sub_category__tariff',
                    'uploaded_by'
                ).prefetch_related('cbc_sample', 'twbc_sample')
            ),
            'appointments',
            'payments'
        )
        return queryset
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(created_at__date=today)
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().filter(created_at__date__range=[start_week, end_week])
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        # ------------------ UPCOMING ENDPOINTS ------------------

    @action(detail=False, methods=['get'])
    def nurse_upcoming(self, request):
        """
        Patients with status 'registered' (waiting for nurse)
        """
        queryset = self.get_queryset().filter(status="Registered").only(
            "id", "first_name", "last_name", "status", "created_at", "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_upcoming(self, request):
        """
        Patients with status 'vital_signed' (waiting for doctor)
        """
        queryset = self.get_queryset().filter(status="vital signs added").only(
            "id", "first_name", "last_name", "status", "created_at", "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def lab_payment(self, request):
        queryset = self.get_queryset().filter(
            Q(status="seen by doctor") &
            (Q(doctor_details__referral_type="lab_only") | Q(doctor_details__referral_type="both"))
        ).distinct()
         # distinct in case multiple doctor_details
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_payment(self, request):
        queryset = self.get_queryset().filter(
            Q(status__in=["lab requested", "injection pending"]) &
            (Q(doctor_details__referral_type="injection_only") | Q(doctor_details__referral_type="both"))
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def injection_upcoming(self, request):
        """
        Patients with status 'injection requested' or 'lab and injection requested'
        """
        statuses = ["injection requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_patient_list(self, request):
        """
        Patients with status 'injection requested', 'lab and injection requested', 'completed'
        """
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_today(self, request):
        today = timezone.now().date()
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date=today
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def injection_weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date__range=[start_week, end_week]
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_monthly(self, request):
        today = timezone.now().date()
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ------------------ LAB ENDPOINTS ------------------

    @action(detail=False, methods=['get'])
    def lab_upcoming(self, request):
        """
        Patients with status 'lab requested' or 'lab and injection requested'
        """
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def lab_today(self, request):
        today = timezone.now().date()
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date=today
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        

    @action(detail=False, methods=['get'])
    def lab_weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date__range=[start_week, end_week]
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def lab_monthly(self, request):
        today = timezone.now().date()
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['get'])
    def doctor_follow_up(self, request):
        """
        Patients for doctor follow-up: 'lab reviewed', 'injection reviewed', 'lab and injection reviewed'
        """
        statuses = ["lab reviewed", "injection reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_lab_follow_up(self, request):
        """
        Patients for doctor lab follow-up: 'lab reviewed', 'lab and injection reviewed'
        """
        statuses = ["lab reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_injection_follow_up(self, request):
        """
        Patients for doctor injection follow-up: 'injection reviewed', 'lab and injection reviewed'
        """
        statuses = ["injection reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def lab_waiting(self, request):
        """
        Patients waiting for lab: 'lab requested', 'lab and injection requested'
        """
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def injection_waiting(self, request):
        """
        Patients waiting for injection: 'injection requested', 'lab and injection requested'
        """
        statuses = ["injection requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def lab_patient_list(self, request):
        """
        Patients in lab patient list: 'lab requested', 'lab and injection requested completed'
        """
        statuses = ["lab requested", "lab and injection requested" ,"completed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()

        # Apply search & filters manually for custom action
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    # ------------------ DOCTOR PATIENT LISTS ------------------

    @action(detail=False, methods=['get'])
    def doctor_all(self, request):
        """
        All doctor patients: all statuses except 'registered'
        """
        queryset = self.get_queryset().exclude(status="registered").only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_today(self, request):
        """
        Doctor patients today: exclude 'registered', filter created today
        """
        today = timezone.now().date()
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__date=today
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_weekly(self, request):
        """
        Doctor patients this week: exclude 'registered', filter by current week
        """
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__date__range=[start_week, end_week]
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_monthly(self, request):
        """
        Doctor patients this month: exclude 'registered', filter by current month
        """
        today = timezone.now().date()
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__year=today.year,
            created_at__month=today.month
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['receptionist'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        registration_tariff = Tariff.objects.get(name="Registration")
        response_data = serializer.data
        response_data['registration_fee'] = {
            "name": registration_tariff.name,
            "price": str(registration_tariff.price)
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        original_receptionist = instance.receptionist
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if 'created_at' in request.data:
            instance.created_at = request.data['created_at']
        self.perform_update(serializer)
        if not request.data.get('receptionist'):
            instance.receptionist = original_receptionist
        instance.save()
        return Response(serializer.data)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print("Serialized data:", serializer.data)  # Add logging to inspect the serialized data
        return Response(serializer.data)
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            'nurse_visit_details',
            'doctor_details__lab_results__cbc_sample',
            'appointments',
            'payments'
        )
        
class PatientNurseDetailsViewSet(viewsets.ModelViewSet):
    queryset = PatientNurseDetails.objects.all()
    serializer_class = PatientNurseDetailsSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'nurse']  # exact matches
    search_fields = ['patient__first_name', 'patient__last_name', 'nurse__first_name']
    ordering_fields = ['id']  # or any valid field
    ordering = ['-id']


    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        nurse_id = self.request.query_params.get('nurse')
        if nurse_id:
            queryset = queryset.filter(nurse_id=nurse_id)
        queryset = queryset.select_related('patient', 'nurse')
        return queryset
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(visit_date=today)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().filter(visit_date__range=[start_week, end_week])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            visit_date__year=today.year,
            visit_date__month=today.month
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming patients from Patient table with status='registered'."""
        upcoming_patients = Patient.objects.filter(status="registered")
        # Reuse PatientSerializer for consistent response
        serializer = PatientSerializer(upcoming_patients, many=True)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['nurse'] = request.user
        patient = serializer.validated_data['patient']
        patient.nurse = serializer.validated_data.get('nurse')
        patient.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.patient.nurse = instance.nurse
        instance.patient.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.patient.nurse = None
        instance.patient.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        queryset = queryset.select_related('employee', 'department')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['employee'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DoctorDetailsViewSet(viewsets.ModelViewSet):
    queryset = DoctorDetails.objects.all()
    serializer_class = DoctorDetailsSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor', 'referral_type']   # exact matches
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name']
    ordering_fields = ['visit_date']   # use fields that exist
    ordering = ['-visit_date']


    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Optimize queries
        queryset = queryset.select_related(
            'patient',
            'doctor'
        ).prefetch_related(
            'medications',
            'injections',
            Prefetch(
                'lab_results',
                queryset=LabResult.objects.select_related(
                    'main_category',
                    'sub_category',
                    'sub_category__tariff',
                    'uploaded_by'
                ).prefetch_related('cbc_sample', 'twbc_sample')
            )
        )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Only set doctor to logged-in user if not provided
        if not serializer.validated_data.get('doctor') and hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['doctor'] = request.user
        patient = serializer.validated_data['patient']
        patient.doctor = serializer.validated_data.get('doctor')
        patient.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        medications_data = request.data.get('medications', [])
        if medications_data:
            for med_data in medications_data:
                CurrentMedication.objects.create(doctor_details=serializer.instance, **med_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance.patient.doctor = instance.doctor
        instance.patient.save()
        self.perform_update(serializer)
        if 'medications' in request.data:
            instance.medications.all().delete()
            medications_data = request.data.get('medications', [])
            for med_data in medications_data:
                CurrentMedication.objects.create(doctor_details=instance, **med_data)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.patient.doctor = None
        instance.patient.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
class CBCSampleViewSet(viewsets.ModelViewSet):
    queryset = CBCSample.objects.all()
    serializer_class = CBCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CBCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A CBC Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TWBCSampleViewSet(viewsets.ModelViewSet):
    queryset = TWBCSample.objects.all()
    serializer_class = TWBCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TWBCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TWBC Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HGBSampleViewSet(viewsets.ModelViewSet):
    queryset = HGBSample.objects.all()
    serializer_class = HGBSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HGBSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A HGB Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ESRSampleViewSet(viewsets.ModelViewSet):
    queryset = ESRSample.objects.all()
    serializer_class = ESRSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ESRSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ESR Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BloodGroupSampleViewSet(viewsets.ModelViewSet):
    queryset = BloodGroupSample.objects.all()
    serializer_class = BloodGroupSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BloodGroupSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Blood Group Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class StoneExamSampleViewSet(viewsets.ModelViewSet):
    queryset = StoneExamSample.objects.all()
    serializer_class = StoneExamSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if StoneExamSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Stone Exam Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ConcentrationSampleViewSet(viewsets.ModelViewSet):
    queryset = ConcentrationSample.objects.all()
    serializer_class = ConcentrationSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ConcentrationSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Concentration Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class OccultBloodSampleViewSet(viewsets.ModelViewSet):
    queryset = OccultBloodSample.objects.all()
    serializer_class = OccultBloodSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if OccultBloodSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An Occult Blood Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PhysicalTestSampleViewSet(viewsets.ModelViewSet):
    queryset = PhysicalTestSample.objects.all()
    serializer_class = PhysicalTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PhysicalTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Physical Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ChemicalTestSampleViewSet(viewsets.ModelViewSet):
    queryset = ChemicalTestSample.objects.all()
    serializer_class = ChemicalTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ChemicalTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Chemical Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class MicroscopicTestSampleViewSet(viewsets.ModelViewSet):
    queryset = MicroscopicTestSample.objects.all()
    serializer_class = MicroscopicTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if MicroscopicTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Microscopic Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCGUrineSampleViewSet(viewsets.ModelViewSet):
    queryset = HCGUrineSample.objects.all()
    serializer_class = HCGUrineSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCGUrineSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCG Urine Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCGSerumSampleViewSet(viewsets.ModelViewSet):
    queryset = HCGSerumSample.objects.all()
    serializer_class = HCGSerumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCGSerumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCG Serum Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class FBSRBSSampleViewSet(viewsets.ModelViewSet):
    queryset = FBSRBSSample.objects.all()
    serializer_class = FBSRBSSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if FBSRBSSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An FBS/RBS Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SGOTASTSampleViewSet(viewsets.ModelViewSet):
    queryset = SGOTASTSample.objects.all()
    serializer_class = SGOTASTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SGOTASTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An SGOT/AST Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SGPTALTSampleViewSet(viewsets.ModelViewSet):
    queryset = SGPTALTSample.objects.all()
    serializer_class = SGPTALTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SGPTALTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An SGPT/ALT Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BilirubinTSampleViewSet(viewsets.ModelViewSet):
    queryset = BilirubinTSample.objects.all()
    serializer_class = BilirubinTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BilirubinTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bilirubin T Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BilirubinDSampleViewSet(viewsets.ModelViewSet):
    queryset = BilirubinDSample.objects.all()
    serializer_class = BilirubinDSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BilirubinDSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bilirubin D Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ALPSampleViewSet(viewsets.ModelViewSet):
    queryset = ALPSample.objects.all()
    serializer_class = ALPSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ALPSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ALP Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CreatinineSampleViewSet(viewsets.ModelViewSet):
    queryset = CreatinineSample.objects.all()
    serializer_class = CreatinineSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CreatinineSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Creatinine Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class UreaSampleViewSet(viewsets.ModelViewSet):
    queryset = UreaSample.objects.all()
    serializer_class = UreaSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if UreaSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Urea Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class UricAcidSampleViewSet(viewsets.ModelViewSet):
    queryset = UricAcidSample.objects.all()
    serializer_class = UricAcidSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if UricAcidSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Uric Acid Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LipaseAmylaseSampleViewSet(viewsets.ModelViewSet):
    queryset = LipaseAmylaseSample.objects.all()
    serializer_class = LipaseAmylaseSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if LipaseAmylaseSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Lipase/Amylase Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TotalCholesterolSampleViewSet(viewsets.ModelViewSet):
    queryset = TotalCholesterolSample.objects.all()
    serializer_class = TotalCholesterolSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TotalCholesterolSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Total Cholesterol Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TriglyceridesSampleViewSet(viewsets.ModelViewSet):
    queryset = TriglyceridesSample.objects.all()
    serializer_class = TriglyceridesSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TriglyceridesSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Triglycerides Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LDLCSampleViewSet(viewsets.ModelViewSet):
    queryset = LDLCSample.objects.all()
    serializer_class = LDLCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if LDLCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An LDL-C Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HDLCSampleViewSet(viewsets.ModelViewSet):
    queryset = HDLCSample.objects.all()
    serializer_class = HDLCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HDLCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HDL-C Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SodiumSampleViewSet(viewsets.ModelViewSet):
    queryset = SodiumSample.objects.all()
    serializer_class = SodiumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SodiumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Sodium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PotassiumSampleViewSet(viewsets.ModelViewSet):
    queryset = PotassiumSample.objects.all()
    serializer_class = PotassiumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PotassiumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Potassium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CalciumSampleViewSet(viewsets.ModelViewSet):
    queryset = CalciumSample.objects.all()
    serializer_class = CalciumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CalciumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Calcium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WidalTestHSampleViewSet(viewsets.ModelViewSet):
    queryset = WidalTestHSample.objects.all()
    serializer_class = WidalTestHSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WidalTestHSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Widal Test H Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WidalTestOSampleViewSet(viewsets.ModelViewSet):
    queryset = WidalTestOSample.objects.all()
    serializer_class = WidalTestOSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WidalTestOSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Widal Test O Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WeilFelixTestSampleViewSet(viewsets.ModelViewSet):
    queryset = WeilFelixTestSample.objects.all()
    serializer_class = WeilFelixTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WeilFelixTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Weil Felix Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class VDRLRPRTestSampleViewSet(viewsets.ModelViewSet):
    queryset = VDRLRPRTestSample.objects.all()
    serializer_class = VDRLRPRTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if VDRLRPRTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A VDRL/RPR Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TPHATestSampleViewSet(viewsets.ModelViewSet):
    queryset = TPHATestSample.objects.all()
    serializer_class = TPHATestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TPHATestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TPHA Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HPyloriAntibodySampleViewSet(viewsets.ModelViewSet):
    queryset = HPyloriAntibodySample.objects.all()
    serializer_class = HPyloriAntibodySampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HPyloriAntibodySample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An H. Pylori Antibody Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HPyloriStoolAntigenSampleViewSet(viewsets.ModelViewSet):
    queryset = HPyloriStoolAntigenSample.objects.all()
    serializer_class = HPyloriStoolAntigenSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HPyloriStoolAntigenSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An H. Pylori Stool Antigen Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HBsAgTestSampleViewSet(viewsets.ModelViewSet):
    queryset = HBsAgTestSample.objects.all()
    serializer_class = HBsAgTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HBsAgTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HBsAg Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCVAgTestSampleViewSet(viewsets.ModelViewSet):
    queryset = HCVAgTestSample.objects.all()
    serializer_class = HCVAgTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCVAgTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCV Ag Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class RheumatoidFactorSampleViewSet(viewsets.ModelViewSet):
    queryset = RheumatoidFactorSample.objects.all()
    serializer_class = RheumatoidFactorSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if RheumatoidFactorSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Rheumatoid Factor Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ASOTiterSampleViewSet(viewsets.ModelViewSet):
    queryset = ASOTiterSample.objects.all()
    serializer_class = ASOTiterSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ASOTiterSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ASO Titer Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class KHBRapidTestSampleViewSet(viewsets.ModelViewSet):
    queryset = KHBRapidTestSample.objects.all()
    serializer_class = KHBRapidTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if KHBRapidTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A KHB Rapid Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class AFBTestSampleViewSet(viewsets.ModelViewSet):
    queryset = AFBTestSample.objects.all()
    serializer_class = AFBTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if AFBTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An AFB Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TBBloodTestSampleViewSet(viewsets.ModelViewSet):
    queryset = TBBloodTestSample.objects.all()
    serializer_class = TBBloodSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TBBloodTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TB Blood Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class GramStainTestSampleViewSet(viewsets.ModelViewSet):
    queryset = GramStainTestSample.objects.all()
    serializer_class = GramStainTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if GramStainTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Gram Stain Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WetMountTestSampleViewSet(viewsets.ModelViewSet):
    queryset = WetMountTestSample.objects.all()
    serializer_class = WetMountTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WetMountTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Wet Mount Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class HETSampleViewSet(viewsets.ModelViewSet):
    queryset = HETSample.objects.all()
    serializer_class = HETSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HETSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A HET Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BodyFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = BodyFluidAnalysisSample.objects.all()
    serializer_class = BodyFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BodyFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Body Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CSFAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = CSFAnalysisSample.objects.all()
    serializer_class = CSFAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CSFAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A CSF Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PeritonealFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = PeritonealFluidAnalysisSample.objects.all()
    serializer_class = PeritonealFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PeritonealFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Peritoneal Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SynovialFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = SynovialFluidAnalysisSample.objects.all()
    serializer_class = SynovialFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SynovialFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Synovial Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BacteriologySampleViewSet(viewsets.ModelViewSet):
    queryset = BacteriologySample.objects.all()
    serializer_class = BacteriologySampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BacteriologySample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bacteriology Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class KOHPreparationSampleViewSet(viewsets.ModelViewSet):
    queryset = KOHPreparationSample.objects.all()
    serializer_class = KOHPreparationSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if KOHPreparationSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A KOH Preparation Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CultureTestSampleViewSet(viewsets.ModelViewSet):
    queryset = CultureTestSample.objects.all()
    serializer_class = CultureTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CultureTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Culture Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
        
class BFSampleViewSet(viewsets.ModelViewSet):
    queryset = BFSample.objects.all()
    serializer_class = BFSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BFSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A BF Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering logic
        doctor_details_id = self.request.query_params.get('doctor_details')
        if doctor_details_id:
            queryset = queryset.filter(doctor_details_id=doctor_details_id)
            
        uploaded_by_id = self.request.query_params.get('uploaded_by')
        if uploaded_by_id:
            queryset = queryset.filter(uploaded_by_id=uploaded_by_id)
        else:
            try:
                if hasattr(self.request, 'user') and self.request.user and isinstance(self.request.user, Employee):
                    queryset = queryset.filter(uploaded_by=self.request.user)
            except AttributeError:
                pass
                
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(doctor_details__patient_id=patient_id)
        
        # Optimize queries - include all sample types prefetch
        queryset = queryset.select_related(
            'doctor_details',
            'main_category',
            'sub_category',
            'sub_category__tariff',
            'uploaded_by'
        ).prefetch_related(
            Prefetch('cbc_sample', queryset=CBCSample.objects.all()),
            Prefetch('twbc_sample', queryset=TWBCSample.objects.all()),
            Prefetch('hgb_sample', queryset=HGBSample.objects.all()),
            Prefetch('esr_sample', queryset=ESRSample.objects.all()),
            Prefetch('blood_group_sample', queryset=BloodGroupSample.objects.all()),
            Prefetch('stone_exam_sample', queryset=StoneExamSample.objects.all()),
            Prefetch('concentration_sample', queryset=ConcentrationSample.objects.all()),
            Prefetch('occult_blood_sample', queryset=OccultBloodSample.objects.all()),
            Prefetch('physical_test_sample', queryset=PhysicalTestSample.objects.all()),
            Prefetch('chemical_test_sample', queryset=ChemicalTestSample.objects.all()),
            Prefetch('microscopic_test_sample', queryset=MicroscopicTestSample.objects.all()),
            Prefetch('hcg_urine_sample', queryset=HCGUrineSample.objects.all()),
            Prefetch('hcg_serum_sample', queryset=HCGSerumSample.objects.all()),
            Prefetch('fbs_rbs_sample', queryset=FBSRBSSample.objects.all()),
            Prefetch('sgot_ast_sample', queryset=SGOTASTSample.objects.all()),
            Prefetch('sgpt_alt_sample', queryset=SGPTALTSample.objects.all()),
            Prefetch('bilirubin_t_sample', queryset=BilirubinTSample.objects.all()),
            Prefetch('bilirubin_d_sample', queryset=BilirubinDSample.objects.all()),
            Prefetch('alp_sample', queryset=ALPSample.objects.all()),
            Prefetch('creatinine_sample', queryset=CreatinineSample.objects.all()),
            Prefetch('urea_sample', queryset=UreaSample.objects.all()),
            Prefetch('uric_acid_sample', queryset=UricAcidSample.objects.all()),
            Prefetch('lipase_amylase_sample', queryset=LipaseAmylaseSample.objects.all()),
            Prefetch('total_cholesterol_sample', queryset=TotalCholesterolSample.objects.all()),
            Prefetch('triglycerides_sample', queryset=TriglyceridesSample.objects.all()),
            Prefetch('ldlc_sample', queryset=LDLCSample.objects.all()),
            Prefetch('hdlc_sample', queryset=HDLCSample.objects.all()),
            Prefetch('sodium_sample', queryset=SodiumSample.objects.all()),
            Prefetch('potassium_sample', queryset=PotassiumSample.objects.all()),
            Prefetch('calcium_sample', queryset=CalciumSample.objects.all()),
            Prefetch('widal_test_h_sample', queryset=WidalTestHSample.objects.all()),
            Prefetch('widal_test_o_sample', queryset=WidalTestOSample.objects.all()),
            Prefetch('weil_felix_test_sample', queryset=WeilFelixTestSample.objects.all()),
            Prefetch('vdrl_rpr_test_sample', queryset=VDRLRPRTestSample.objects.all()),
            Prefetch('tpha_test_sample', queryset=TPHATestSample.objects.all()),
            Prefetch('h_pylori_antibody_sample', queryset=HPyloriAntibodySample.objects.all()),
            Prefetch('h_pylori_stool_antigen_sample', queryset=HPyloriStoolAntigenSample.objects.all()),
            Prefetch('hbsag_test_sample', queryset=HBsAgTestSample.objects.all()),
            Prefetch('hcv_ag_test_sample', queryset=HCVAgTestSample.objects.all()),
            Prefetch('rheumatoid_factor_sample', queryset=RheumatoidFactorSample.objects.all()),
            Prefetch('aso_titer_sample', queryset=ASOTiterSample.objects.all()),
            Prefetch('khb_rapid_test_sample', queryset=KHBRapidTestSample.objects.all()),
            Prefetch('afb_test_sample', queryset=AFBTestSample.objects.all()),
            Prefetch('tb_blood_test_sample', queryset=TBBloodTestSample.objects.all()),
            Prefetch('gram_stain_test_sample', queryset=GramStainTestSample.objects.all()),
            Prefetch('wet_mount_test_sample', queryset=WetMountTestSample.objects.all()),
            Prefetch('koh_preparation_sample', queryset=KOHPreparationSample.objects.all()),
            Prefetch('culture_test_sample', queryset=CultureTestSample.objects.all()),
            Prefetch('het_sample', queryset=HETSample.objects.all()),
            Prefetch('body_fluid_analysis_sample', queryset=BodyFluidAnalysisSample.objects.all()),
            Prefetch('csf_analysis_sample', queryset=CSFAnalysisSample.objects.all()),
            Prefetch('peritoneal_fluid_analysis_sample', queryset=PeritonealFluidAnalysisSample.objects.all()),
            Prefetch('synovial_fluid_analysis_sample', queryset=SynovialFluidAnalysisSample.objects.all()),
            Prefetch('bacteriology_sample', queryset=BacteriologySample.objects.all()),
            Prefetch('bf_sample', queryset=BFSample.objects.all()),
        )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()
        lab_result = serializer.instance
        self._create_related_samples(lab_result)

    def perform_update(self, serializer):
        lab_result = serializer.save()
        self._create_related_samples(lab_result)

    def _create_related_samples(self, lab_result):
        """Helper method to create related samples based on sub_category"""
        if not lab_result.sub_category:
            return

        sub_category_name = lab_result.sub_category.name
        sample_creators = {
            "CBC": lambda: CBCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="CBC",
                wbc=0,
                rbc=0,
                hgb=0,
                hct=0,
                mcv=0,
                mch=0,
                mchc=0,
                rdw_cv=0,
                rdw_sd=0,
                plt=0,
                mpv=0,
                pdw=0,
                pct=0,
                p_lcr=0,
                p_lcc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TWBC": lambda: TWBCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="TWBC",
                wbc=0,
                lymph_percent=0,
                lymph_absolute=0,
                gran_percent=0,
                gran_absolute=0,
                mid_percent=0,
                mid_absolute=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HGB": lambda: HGBSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HGB",
                hgb=0,
                rbc=0,
                hct=0,
                mcv=0,
                mch=0,
                mchc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ESR": lambda: ESRSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="ESR",
                esr=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Blood Group": lambda: BloodGroupSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Blood Group",
                blood_group="",
                rh_factor="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Stone Exam": lambda: StoneExamSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Stone Exam",
                stone_type="",
                color="",
                consistency="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Concentration Test": lambda: ConcentrationSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Concentration Test",
                color="",
                appearance="",
                volume=0,
                reaction_ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Occult Blood": lambda: OccultBloodSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Occult Blood",
                occult_blood_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Physical Test": lambda: PhysicalTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Physical Test",
                color="",
                appearance="",
                volume=0,
                reaction_ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Chemical Test": lambda: ChemicalTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Chemical Test",
                protein="",
                glucose="",
                ketone="",
                bilirubin="",
                urobilinogen="",
                blood="",
                nitrite="",
                leukocyte_esterase="",
                ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Microscopic Test": lambda: MicroscopicTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Microscopic Test",
                rbcs="",
                wbcs="",
                epithelial_cells="",
                casts="",
                crystals="",
                bacteria="",
                yeast="",
                parasites="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCG Urine": lambda: HCGUrineSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HCG Urine",
                hcg_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCG Serum": lambda: HCGSerumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HCG Serum",
                hcg_level=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "FBS/RBS": lambda: FBSRBSSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="FBS/RBS",
                test_type="",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "SGOT/AST": lambda: SGOTASTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="SGOT/AST",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "SGPT/ALT": lambda: SGPTALTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="SGPT/ALT",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bilirubin Total": lambda: BilirubinTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Bilirubin Total",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bilirubin Direct": lambda: BilirubinDSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Bilirubin Direct",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ALP": lambda: ALPSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="ALP",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Creatinine": lambda: CreatinineSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Creatinine",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Urea": lambda: UreaSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Urea",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Uric Acid": lambda: UricAcidSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Uric Acid",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Lipase/Amylase": lambda: LipaseAmylaseSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Lipase/Amylase",
                lipase_result=0,
                lipase_reference="",
                amylase_result=0,
                amylase_reference="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Total Cholesterol": lambda: TotalCholesterolSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Total Cholesterol",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Triglycerides": lambda: TriglyceridesSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Triglycerides",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "LDL-C": lambda: LDLCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="LDL-C",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HDL-C": lambda: HDLCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HDL-C",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Sodium": lambda: SodiumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Sodium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Potassium": lambda: PotassiumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Potassium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Calcium": lambda: CalciumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Calcium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Widal Test H": lambda: WidalTestHSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Widal Test H",
                widal_h_antigen_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Widal Test O": lambda: WidalTestOSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Widal Test O",
                widal_o_antigen_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Weil Felix Test": lambda: WeilFelixTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Weil Felix Test",
                antigen_ox19_titer="",
                antigen_ox2_titer="",
                antigen_oxk_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "VDRL/RPR Test": lambda: VDRLRPRTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="VDRL/RPR Test",
                test_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TPHA Test": lambda: TPHATestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="TPHA Test",
                tpha_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "H. Pylori Antibody": lambda: HPyloriAntibodySample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="H. Pylori Antibody",
                antibody_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "H. Pylori Stool Antigen": lambda: HPyloriStoolAntigenSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="H. Pylori Stool Antigen",
                stool_antigen_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HBsAg Test": lambda: HBsAgTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="HBsAg Test",
                hbsag_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCVAg Test": lambda: HCVAgTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="HCVAg Test",
                hcvag_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Rheumatoid Factor": lambda: RheumatoidFactorSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Rheumatoid Factor",
                rf_result="",
                rf_value=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ASO Titer": lambda: ASOTiterSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="ASO Titer",
                aso_titer=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "KHB Rapid Test": lambda: KHBRapidTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="KHB Rapid Test",
                rapid_test_result="",
                test_type="",
                method_used="",
                reference_range="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "AFB Test": lambda: AFBTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="AFB Test",
                spot_sample_result="",
                morning_sample_result="",
                second_spot_sample_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TB Blood Test": lambda: TBBloodTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="TB Blood Test",
                tb_blood_test_result="",
                method_used="",
                reference_range="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Gram Stain Test": lambda: GramStainTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Gram Stain Test",
                sample_type="",
                organism_type="",
                cellular_elements="",
                background="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Wet Mount Test": lambda: WetMountTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Wet Mount Test",
                sample_type="",
                organisms_observed="",
                motility="",
                pus_cells="",
                rbcs="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "KOH Preparation": lambda: KOHPreparationSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="KOH Preparation",
                sample_type="",
                fungal_elements="",
                yeast_cells="",
                pseudohyphae="",
                background="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Culture Test": lambda: CultureTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Culture Test",
                sample_type="",
                organism_isolated="",
                growth_description="",
                antibiotic_sensitivity="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HET": lambda: HETSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HET",
                het=0,
                hgb=0,
                rbc=0,
                mcv=0,
                mch=0,
                mchc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Body Fluid Analysis": lambda: BodyFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Body Fluid Analysis",
                fluid_type="",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "CSF Analysis": lambda: CSFAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="CSF Analysis",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                chloride=0,
                opening_pressure=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Peritoneal Fluid Analysis": lambda: PeritonealFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Peritoneal Fluid Analysis",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                ldh=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Synovial Fluid Analysis": lambda: SynovialFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Synovial Fluid Analysis",
                appearance="",
                viscosity="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                crystals="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bacteriology": lambda: BacteriologySample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Bacteriology",
                sample_type="",
                culture_result="",
                colony_count="",
                antibiotic_sensitivity_pattern="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "BF": lambda: BFSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="BF",
                parasite_seen=None,
                parasite_species="",
                parasite_stage="",
                parasite_density=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
        }

        creator = sample_creators.get(sub_category_name)
        if creator and not hasattr(lab_result, f"{sub_category_name.lower().replace(' ', '_')}_sample"):
            creator()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if not serializer.validated_data.get('uploaded_by') and hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['uploaded_by'] = request.user
            else:
                if 'uploaded_by' not in serializer.validated_data:
                    return Response({"error": "uploaded_by is required if user is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"error": "Invalid request object"}, status=status.HTTP_400_BAD_REQUEST)
        doctor_details_id = serializer.validated_data['doctor_details']
        doctor_details = get_object_or_404(DoctorDetails, id=doctor_details_id.id)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InjectionRoom, DoctorDetails, Employee
from .serializers import InjectionRoomSerializer
from django.db.models import Sum, Count
from django.utils.timezone import now
import calendar

class InjectionRoomViewSet(viewsets.ModelViewSet):
    queryset = InjectionRoom.objects.all()
    serializer_class = InjectionRoomSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor_details', 'nurse', 'doctor_details__patient']  # nested lookups allowed
    search_fields = ['doctor_details__patient__first_name', 'doctor_details__patient__last_name', 'nurse__first_name']
    ordering_fields = ['id']  
    ordering = ['-id']


    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(doctor_details__patient=patient_id)
        doctor_details_id = self.request.query_params.get('doctor_details')
        if doctor_details_id:
            queryset = queryset.filter(doctor_details_id=doctor_details_id)
        nurse_id = self.request.query_params.get('nurse')
        if nurse_id:
            queryset = queryset.filter(nurse_id=nurse_id)
        if hasattr(self.request.user, 'id') and isinstance(self.request.user, Employee):
            queryset = queryset.filter(doctor_details__referral_type__in=['injection_only', 'both'])
        queryset = queryset.select_related(
            'doctor_details',
            'doctor_details__doctor',
            'nurse'
        ).prefetch_related('doctor_details__patient')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor_details_id = serializer.validated_data.get('doctor_details')
        doctor_details = get_object_or_404(DoctorDetails, id=doctor_details_id.id)
        if doctor_details.referral_type not in ['injection_only', 'both']:
            return Response(
                {"error": "This visit has not been referred to the injection room"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        appointed_by_id = self.request.query_params.get('appointed_by')
        if appointed_by_id:
            queryset = queryset.filter(appointed_by_id=appointed_by_id)
        queryset = queryset.select_related('patient', 'appointed_by')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
            serializer.validated_data['appointed_by'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
            serializer.validated_data['appointed_by'] = request.user
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'receptionist']
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__phone_number',
        'receptionist_name',
    ]
    ordering_fields = ['id', 'payment_amount', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'receptionist')

    def filter_custom_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    # ------------------ REPORT ENDPOINTS WITH PAGINATION ------------------

    @action(detail=False, methods=['get'])
    def all_payments(self, request):
        queryset = self.filter_custom_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        totals = queryset.aggregate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def today_payment(self, request):
        today = now().date()
        queryset = self.filter_custom_queryset(
            self.get_queryset().filter(created_at__date=today)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        totals = queryset.aggregate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "date": str(today),
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "date": str(today),
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def weekly_payment(self, request):
        today = now().date()
        start_week = today - timedelta(days=today.weekday())  # Monday
        end_week = start_week + timedelta(days=6)  # Sunday

        queryset = self.get_queryset().filter(created_at__date__range=[start_week, end_week])

        # Filter by weekday if requested
        weekday = request.query_params.get("day")  # e.g. Monday, Tuesday
        if weekday:
            weekday_map = {
                "sunday": 1, "monday": 2, "tuesday": 3,
                "wednesday": 4, "thursday": 5, "friday": 6, "saturday": 7
            }
            day_num = weekday_map.get(weekday.lower())
            if day_num:
                queryset = queryset.filter(created_at__week_day=day_num)

        queryset = self.filter_custom_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        breakdown = queryset.values("created_at__week_day") \
                            .annotate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        day_map = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
                   5: "Thursday", 6: "Friday", 7: "Saturday"}
        breakdown_list = [
            {"day": day_map[item["created_at__week_day"]],
             "total_amount": item["total_amount"] or 0,
             "total_count": item["total_count"]}
            for item in breakdown
        ]

        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "week_start": str(start_week),
            "week_end": str(end_week),
            "breakdown": breakdown_list,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "week_start": str(start_week),
            "week_end": str(end_week),
            "breakdown": breakdown_list,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def monthly_payment(self, request):
        year = now().year
        queryset = self.get_queryset().filter(created_at__year=year)

        month = request.query_params.get("month")  # e.g. September, 9
        if month:
            try:
                if month.isdigit():
                    month_num = int(month)
                else:
                    month_num = list(calendar.month_name).index(month.capitalize())
                queryset = queryset.filter(created_at__month=month_num)
            except Exception:
                pass

        queryset = self.filter_custom_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        breakdown = queryset.values("created_at__month") \
                            .annotate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        results = [
            {"month": calendar.month_name[item["created_at__month"]],
             "total_amount": item["total_amount"] or 0,
             "total_count": item["total_count"]}
            for item in breakdown
        ]

        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "year": year,
            "breakdown": results,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "year": year,
            "breakdown": results,
            "per_patient": list(per_patient),
            "data": data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['receptionist'] = request.user
            else:
                if 'receptionist' not in serializer.validated_data:
                    return Response({"error": "receptionist is required if user is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"error": "Invalid request object"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)

        instance = serializer.instance
        instance = Payment.objects.select_related("patient", "receptionist").get(pk=instance.pk)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['receptionist'] = request.user
        except AttributeError:
            pass
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('subcategories')
        return queryset

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        main_category_id = self.request.query_params.get('main_category')
        if main_category_id:
            queryset = queryset.filter(main_category_id=main_category_id)
        queryset = queryset.select_related('main_category', 'tariff')
        return queryset

class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        queryset = queryset.select_related('category')
        return queryset

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    pagination_class = None
    filter_backends = []

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        queryset = queryset.select_related('patient', 'doctor')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee) and request.user.role == 'Doctor':
            serializer.validated_data['doctor'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee) and request.user.role == 'Doctor':
            serializer.validated_data['doctor'] = request.user
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
class MedicationPriceViewSet(viewsets.ModelViewSet):
    queryset = MedicationPrice.objects.all()
    serializer_class = MedicationPriceSerializer

    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        queryset = super().get_queryset()
        tariff_id = self.request.query_params.get('tariff')
        if tariff_id:
            queryset = queryset.filter(tariff_id=tariff_id)
        queryset = queryset.select_related('tariff')
        return queryset

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    pagination_class = None
    filter_backends = []
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    EmployeeSerializer, LoginSerializer, TokenRefreshSerializer, RoleSerializer, PatientSerializer,
    PatientNurseDetailsSerializer, DoctorSerializer, DoctorDetailsSerializer, LabResultSerializer,
    InjectionRoomSerializer, DepartmentSerializer, AppointmentSerializer, PaymentSerializer,
    CategorySerializer, SubCategorySerializer, LabTestSerializer, TariffSerializer, MedicationSerializer , CBCSampleSerializer , TWBCSampleSerializer, HGBSampleSerializer ,ESRSampleSerializer, BloodGroupSampleSerializer, StoneExamSampleSerializer, ConcentrationSampleSerializer, OccultBloodSampleSerializer, PhysicalTestSampleSerializer, ChemicalTestSampleSerializer, MicroscopicTestSampleSerializer, HCGUrineSampleSerializer, HCGSerumSampleSerializer, FBSRBSSampleSerializer, SGOTASTSampleSerializer, SGPTALTSampleSerializer, BilirubinTSampleSerializer, BilirubinDSampleSerializer, ALPSampleSerializer, CreatinineSampleSerializer, UreaSampleSerializer, UricAcidSampleSerializer, LipaseAmylaseSampleSerializer, TotalCholesterolSampleSerializer, TriglyceridesSampleSerializer, LDLCSampleSerializer, HDLCSampleSerializer, SodiumSampleSerializer, PotassiumSampleSerializer , KHBRapidTestSampleSerializer , AFBTestSampleSerializer,
    CalciumSampleSerializer, WidalTestHSampleSerializer, WidalTestOSampleSerializer, WeilFelixTestSampleSerializer, VDRLRPRTestSampleSerializer, TPHATestSampleSerializer, HPyloriAntibodySampleSerializer, HPyloriStoolAntigenSampleSerializer, HBsAgTestSampleSerializer, HCVAgTestSampleSerializer, RheumatoidFactorSampleSerializer, ASOTiterSampleSerializer, TBBloodSampleSerializer , GramStainTestSampleSerializer , WetMountTestSampleSerializer, KOHPreparationSampleSerializer, CultureTestSampleSerializer,
    HETSampleSerializer, BodyFluidAnalysisSampleSerializer,
    CSFAnalysisSampleSerializer, PeritonealFluidAnalysisSampleSerializer,
    SynovialFluidAnalysisSampleSerializer, BacteriologySampleSerializer ,MedicationPriceSerializer, MaterialSerializer,BFSampleSerializer
)
from django.db.models import Prefetch
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from .models import (
    Employee, Patient, Role, PatientNurseDetails, Doctor, DoctorDetails, CurrentMedication,
    Medication, LabResult, InjectionRoom, Department, Appointment, Payment, Category, SubCategory, LabTest, Tariff ,
    HETSample, BodyFluidAnalysisSample,
    CSFAnalysisSample, PeritonealFluidAnalysisSample, SynovialFluidAnalysisSample,
    BacteriologySample ,MedicationPrice, Material 
    )
from .models import Department  , Tariff , Medication ,CBCSample ,TWBCSample ,HGBSample ,ESRSample,BloodGroupSample,StoneExamSample,ConcentrationSample,OccultBloodSample ,PhysicalTestSample ,ChemicalTestSample,MicroscopicTestSample,HCGUrineSample,HCGSerumSample,FBSRBSSample,SGOTASTSample,SGPTALTSample,BilirubinTSample,BilirubinDSample,ALPSample,CreatinineSample,UreaSample,UricAcidSample,LipaseAmylaseSample,TotalCholesterolSample,TriglyceridesSample,LDLCSample,HDLCSample,SodiumSample,PotassiumSample, CalciumSample , WidalTestHSample , WidalTestOSample,WeilFelixTestSample,VDRLRPRTestSample,TPHATestSample ,HPyloriAntibodySample,HPyloriStoolAntigenSample,HBsAgTestSample,HCVAgTestSample,RheumatoidFactorSample, ASOTiterSample,KHBRapidTestSample,AFBTestSample, TBBloodTestSample,GramStainTestSample,WetMountTestSample,KOHPreparationSample,CultureTestSample,BFSample
from django.http import Http404 
from rest_framework import views, viewsets , filters
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect , render
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        queryset = queryset.select_related('department')
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmployeeRegistrationView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        refresh = RefreshToken.for_user(employee)
        return Response({
            'employee': EmployeeSerializer(employee).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            employee = Employee.objects.get(email=email)
            if employee.check_password(password):
                refresh = RefreshToken.for_user(employee)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'employee': EmployeeSerializer(employee).data
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Employee.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class TokenRefreshView(generics.GenericAPIView):
    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class PasswordResetRequestView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            employee = Employee.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(employee.pk))
            token = default_token_generator.make_token(employee)
            reset_link = f"http://127.0.0.1:8000/api/reset/{uid}/{token}/"
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=True,
            )
            return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            employee = Employee.objects.get(pk=uid)
            if default_token_generator.check_token(employee, token):
                new_password = request.data.get('new_password')
                if not new_password:
                    return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
                employee.set_password(new_password)
                employee.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, Employee.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

def create_patient(request):
    if request.method == 'POST':
        department_id = request.POST.get('department')
        department = Department.objects.get(id=department_id) if department_id else None
        patient = Patient.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
            department=department,
        )
        return redirect('patient_list')
    return render(request, 'create_patient.html', {'departments': Department.objects.all()})

class EmployeeListView(ListAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        email = self.request.GET.get('email')
        queryset = Employee.objects.all()
        if email:
            return queryset.filter(email=email)
        return queryset

class EmployeeDetailView(generics.RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'id'

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

@api_view(['POST'])
def logout_view(request):
    response = Response({"message": "Logged out successfully"}, status=200)
    response.delete_cookie("jwt")
    return response
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['receptionist', 'nurse', 'doctor', 'department']  
    search_fields = ['first_name', 'last_name', 'phone_number']  
    ordering_fields = ['created_at', 'updated_at']  
    ordering = ['-created_at'] 

    def get_queryset(self):
        queryset = super().get_queryset()
        # Your existing filtering logic...
        
        # Optimize queries for patient details
        queryset = queryset.select_related(
            'receptionist', 'nurse', 'doctor', 'department'
        ).prefetch_related(
            'nurse_visit_details',
            Prefetch(
                'doctor_details__lab_results',
                queryset=LabResult.objects.select_related(
                    'main_category',
                    'sub_category',
                    'sub_category__tariff',
                    'uploaded_by'
                ).prefetch_related('cbc_sample', 'twbc_sample')
            ),
            'appointments',
            'payments'
        )
        return queryset
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(created_at__date=today)
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().filter(created_at__date__range=[start_week, end_week])
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        # ------------------ UPCOMING ENDPOINTS ------------------

    @action(detail=False, methods=['get'])
    def nurse_upcoming(self, request):
        """
        Patients with status 'registered' (waiting for nurse)
        """
        queryset = self.get_queryset().filter(status="Registered").only(
            "id", "first_name", "last_name", "status", "created_at", "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_upcoming(self, request):
        """
        Patients with status 'vital_signed' (waiting for doctor)
        """
        queryset = self.get_queryset().filter(status="vital signs added").only(
            "id", "first_name", "last_name", "status", "created_at", "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def lab_payment(self, request):
        queryset = self.get_queryset().filter(
            Q(status="seen by doctor") &
            (Q(doctor_details__referral_type="lab_only") | Q(doctor_details__referral_type="both"))
        ).distinct()
         # distinct in case multiple doctor_details
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_payment(self, request):
        queryset = self.get_queryset().filter(
            Q(status__in=["lab requested", "injection pending"]) &
            (Q(doctor_details__referral_type="injection_only") | Q(doctor_details__referral_type="both"))
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def injection_upcoming(self, request):
        """
        Patients with status 'injection requested' or 'lab and injection requested'
        """
        statuses = ["injection requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_patient_list(self, request):
        """
        Patients with status 'injection requested', 'lab and injection requested', 'completed'
        """
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_today(self, request):
        today = timezone.now().date()
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date=today
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def injection_weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date__range=[start_week, end_week]
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def injection_monthly(self, request):
        today = timezone.now().date()
        statuses = ["injection requested", "lab and injection requested", "completed"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # ------------------ LAB ENDPOINTS ------------------

    @action(detail=False, methods=['get'])
    def lab_upcoming(self, request):
        """
        Patients with status 'lab requested' or 'lab and injection requested'
        """
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def lab_today(self, request):
        today = timezone.now().date()
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date=today
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        

    @action(detail=False, methods=['get'])
    def lab_weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__date__range=[start_week, end_week]
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'])
    def lab_monthly(self, request):
        today = timezone.now().date()
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(
            status__in=statuses,
            created_at__year=today.year,
            created_at__month=today.month
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['get'])
    def doctor_follow_up(self, request):
        """
        Patients for doctor follow-up: 'lab reviewed', 'injection reviewed', 'lab and injection reviewed'
        """
        statuses = ["lab reviewed", "injection reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_lab_follow_up(self, request):
        """
        Patients for doctor lab follow-up: 'lab reviewed', 'lab and injection reviewed'
        """
        statuses = ["lab reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def doctor_injection_follow_up(self, request):
        """
        Patients for doctor injection follow-up: 'injection reviewed', 'lab and injection reviewed'
        """
        statuses = ["injection reviewed", "lab and injection reviewed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def lab_waiting(self, request):
        """
        Patients waiting for lab: 'lab requested', 'lab and injection requested'
        """
        statuses = ["lab requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def injection_waiting(self, request):
        """
        Patients waiting for injection: 'injection requested', 'lab and injection requested'
        """
        statuses = ["injection requested", "lab and injection requested"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def lab_patient_list(self, request):
        """
        Patients in lab patient list: 'lab requested', 'lab and injection requested completed'
        """
        statuses = ["lab requested", "lab and injection requested" ,"completed"]
        queryset = self.get_queryset().filter(status__in=statuses).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        ).distinct()

        # Apply search & filters manually for custom action
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    # ------------------ DOCTOR PATIENT LISTS ------------------

    @action(detail=False, methods=['get'])
    def doctor_all(self, request):
        """
        All doctor patients: all statuses except 'registered'
        """
        queryset = self.get_queryset().exclude(status="registered").only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_today(self, request):
        """
        Doctor patients today: exclude 'registered', filter created today
        """
        today = timezone.now().date()
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__date=today
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_weekly(self, request):
        """
        Doctor patients this week: exclude 'registered', filter by current week
        """
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__date__range=[start_week, end_week]
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'])
    def doctor_monthly(self, request):
        """
        Doctor patients this month: exclude 'registered', filter by current month
        """
        today = timezone.now().date()
        queryset = self.get_queryset().exclude(status="registered").filter(
            created_at__year=today.year,
            created_at__month=today.month
        ).only(
            "id", "first_name", "last_name", "status", "created_at",
            "receptionist_id", "nurse_id", "doctor_id"
        )
        for backend in (DjangoFilterBackend(), filters.SearchFilter()):
            queryset = backend.filter_queryset(self.request, queryset, self)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.get_serializer(queryset, many=True).data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['receptionist'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        registration_tariff = Tariff.objects.get(name="Registration")
        response_data = serializer.data
        response_data['registration_fee'] = {
            "name": registration_tariff.name,
            "price": str(registration_tariff.price)
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        original_receptionist = instance.receptionist
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if 'created_at' in request.data:
            instance.created_at = request.data['created_at']
        self.perform_update(serializer)
        if not request.data.get('receptionist'):
            instance.receptionist = original_receptionist
        instance.save()
        return Response(serializer.data)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print("Serialized data:", serializer.data)  # Add logging to inspect the serialized data
        return Response(serializer.data)
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related(
            'nurse_visit_details',
            'doctor_details__lab_results__cbc_sample',
            'appointments',
            'payments'
        )
        
class PatientNurseDetailsViewSet(viewsets.ModelViewSet):
    queryset = PatientNurseDetails.objects.all()
    serializer_class = PatientNurseDetailsSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'nurse']  # exact matches
    search_fields = ['patient__first_name', 'patient__last_name', 'nurse__first_name']
    ordering_fields = ['id']  # or any valid field
    ordering = ['-id']


    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        nurse_id = self.request.query_params.get('nurse')
        if nurse_id:
            queryset = queryset.filter(nurse_id=nurse_id)
        queryset = queryset.select_related('patient', 'nurse')
        return queryset
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(visit_date=today)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def weekly(self, request):
        today = timezone.now().date()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        queryset = self.get_queryset().filter(visit_date__range=[start_week, end_week])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly(self, request):
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            visit_date__year=today.year,
            visit_date__month=today.month
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming patients from Patient table with status='registered'."""
        upcoming_patients = Patient.objects.filter(status="registered")
        # Reuse PatientSerializer for consistent response
        serializer = PatientSerializer(upcoming_patients, many=True)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['nurse'] = request.user
        patient = serializer.validated_data['patient']
        patient.nurse = serializer.validated_data.get('nurse')
        patient.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.patient.nurse = instance.nurse
        instance.patient.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.patient.nurse = None
        instance.patient.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        queryset = queryset.select_related('employee', 'department')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['employee'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DoctorDetailsViewSet(viewsets.ModelViewSet):
    queryset = DoctorDetails.objects.all()
    serializer_class = DoctorDetailsSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor', 'referral_type']   # exact matches
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__first_name', 'doctor__last_name']
    ordering_fields = ['visit_date']   # use fields that exist
    ordering = ['-visit_date']


    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        
        # Optimize queries
        queryset = queryset.select_related(
            'patient',
            'doctor'
        ).prefetch_related(
            'medications',
            'injections',
            Prefetch(
                'lab_results',
                queryset=LabResult.objects.select_related(
                    'main_category',
                    'sub_category',
                    'sub_category__tariff',
                    'uploaded_by'
                ).prefetch_related('cbc_sample', 'twbc_sample')
            )
        )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Only set doctor to logged-in user if not provided
        if not serializer.validated_data.get('doctor') and hasattr(request.user, 'id') and isinstance(request.user, Employee):
            serializer.validated_data['doctor'] = request.user
        patient = serializer.validated_data['patient']
        patient.doctor = serializer.validated_data.get('doctor')
        patient.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        medications_data = request.data.get('medications', [])
        if medications_data:
            for med_data in medications_data:
                CurrentMedication.objects.create(doctor_details=serializer.instance, **med_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance.patient.doctor = instance.doctor
        instance.patient.save()
        self.perform_update(serializer)
        if 'medications' in request.data:
            instance.medications.all().delete()
            medications_data = request.data.get('medications', [])
            for med_data in medications_data:
                CurrentMedication.objects.create(doctor_details=instance, **med_data)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.patient.doctor = None
        instance.patient.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
class CBCSampleViewSet(viewsets.ModelViewSet):
    queryset = CBCSample.objects.all()
    serializer_class = CBCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CBCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A CBC Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TWBCSampleViewSet(viewsets.ModelViewSet):
    queryset = TWBCSample.objects.all()
    serializer_class = TWBCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TWBCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TWBC Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HGBSampleViewSet(viewsets.ModelViewSet):
    queryset = HGBSample.objects.all()
    serializer_class = HGBSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HGBSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A HGB Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ESRSampleViewSet(viewsets.ModelViewSet):
    queryset = ESRSample.objects.all()
    serializer_class = ESRSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ESRSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ESR Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BloodGroupSampleViewSet(viewsets.ModelViewSet):
    queryset = BloodGroupSample.objects.all()
    serializer_class = BloodGroupSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BloodGroupSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Blood Group Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class StoneExamSampleViewSet(viewsets.ModelViewSet):
    queryset = StoneExamSample.objects.all()
    serializer_class = StoneExamSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if StoneExamSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Stone Exam Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ConcentrationSampleViewSet(viewsets.ModelViewSet):
    queryset = ConcentrationSample.objects.all()
    serializer_class = ConcentrationSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ConcentrationSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Concentration Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class OccultBloodSampleViewSet(viewsets.ModelViewSet):
    queryset = OccultBloodSample.objects.all()
    serializer_class = OccultBloodSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if OccultBloodSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An Occult Blood Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PhysicalTestSampleViewSet(viewsets.ModelViewSet):
    queryset = PhysicalTestSample.objects.all()
    serializer_class = PhysicalTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PhysicalTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Physical Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ChemicalTestSampleViewSet(viewsets.ModelViewSet):
    queryset = ChemicalTestSample.objects.all()
    serializer_class = ChemicalTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ChemicalTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Chemical Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class MicroscopicTestSampleViewSet(viewsets.ModelViewSet):
    queryset = MicroscopicTestSample.objects.all()
    serializer_class = MicroscopicTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if MicroscopicTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Microscopic Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCGUrineSampleViewSet(viewsets.ModelViewSet):
    queryset = HCGUrineSample.objects.all()
    serializer_class = HCGUrineSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCGUrineSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCG Urine Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCGSerumSampleViewSet(viewsets.ModelViewSet):
    queryset = HCGSerumSample.objects.all()
    serializer_class = HCGSerumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCGSerumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCG Serum Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class FBSRBSSampleViewSet(viewsets.ModelViewSet):
    queryset = FBSRBSSample.objects.all()
    serializer_class = FBSRBSSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if FBSRBSSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An FBS/RBS Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SGOTASTSampleViewSet(viewsets.ModelViewSet):
    queryset = SGOTASTSample.objects.all()
    serializer_class = SGOTASTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SGOTASTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An SGOT/AST Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SGPTALTSampleViewSet(viewsets.ModelViewSet):
    queryset = SGPTALTSample.objects.all()
    serializer_class = SGPTALTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SGPTALTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An SGPT/ALT Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BilirubinTSampleViewSet(viewsets.ModelViewSet):
    queryset = BilirubinTSample.objects.all()
    serializer_class = BilirubinTSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BilirubinTSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bilirubin T Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BilirubinDSampleViewSet(viewsets.ModelViewSet):
    queryset = BilirubinDSample.objects.all()
    serializer_class = BilirubinDSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BilirubinDSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bilirubin D Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ALPSampleViewSet(viewsets.ModelViewSet):
    queryset = ALPSample.objects.all()
    serializer_class = ALPSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ALPSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ALP Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CreatinineSampleViewSet(viewsets.ModelViewSet):
    queryset = CreatinineSample.objects.all()
    serializer_class = CreatinineSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CreatinineSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Creatinine Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class UreaSampleViewSet(viewsets.ModelViewSet):
    queryset = UreaSample.objects.all()
    serializer_class = UreaSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if UreaSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Urea Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class UricAcidSampleViewSet(viewsets.ModelViewSet):
    queryset = UricAcidSample.objects.all()
    serializer_class = UricAcidSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if UricAcidSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Uric Acid Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LipaseAmylaseSampleViewSet(viewsets.ModelViewSet):
    queryset = LipaseAmylaseSample.objects.all()
    serializer_class = LipaseAmylaseSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if LipaseAmylaseSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Lipase/Amylase Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TotalCholesterolSampleViewSet(viewsets.ModelViewSet):
    queryset = TotalCholesterolSample.objects.all()
    serializer_class = TotalCholesterolSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TotalCholesterolSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Total Cholesterol Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TriglyceridesSampleViewSet(viewsets.ModelViewSet):
    queryset = TriglyceridesSample.objects.all()
    serializer_class = TriglyceridesSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TriglyceridesSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Triglycerides Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LDLCSampleViewSet(viewsets.ModelViewSet):
    queryset = LDLCSample.objects.all()
    serializer_class = LDLCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if LDLCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An LDL-C Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HDLCSampleViewSet(viewsets.ModelViewSet):
    queryset = HDLCSample.objects.all()
    serializer_class = HDLCSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HDLCSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HDL-C Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SodiumSampleViewSet(viewsets.ModelViewSet):
    queryset = SodiumSample.objects.all()
    serializer_class = SodiumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SodiumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Sodium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PotassiumSampleViewSet(viewsets.ModelViewSet):
    queryset = PotassiumSample.objects.all()
    serializer_class = PotassiumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PotassiumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Potassium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CalciumSampleViewSet(viewsets.ModelViewSet):
    queryset = CalciumSample.objects.all()
    serializer_class = CalciumSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CalciumSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Calcium Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WidalTestHSampleViewSet(viewsets.ModelViewSet):
    queryset = WidalTestHSample.objects.all()
    serializer_class = WidalTestHSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WidalTestHSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Widal Test H Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WidalTestOSampleViewSet(viewsets.ModelViewSet):
    queryset = WidalTestOSample.objects.all()
    serializer_class = WidalTestOSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WidalTestOSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Widal Test O Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WeilFelixTestSampleViewSet(viewsets.ModelViewSet):
    queryset = WeilFelixTestSample.objects.all()
    serializer_class = WeilFelixTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WeilFelixTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Weil Felix Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class VDRLRPRTestSampleViewSet(viewsets.ModelViewSet):
    queryset = VDRLRPRTestSample.objects.all()
    serializer_class = VDRLRPRTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if VDRLRPRTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A VDRL/RPR Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TPHATestSampleViewSet(viewsets.ModelViewSet):
    queryset = TPHATestSample.objects.all()
    serializer_class = TPHATestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TPHATestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TPHA Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HPyloriAntibodySampleViewSet(viewsets.ModelViewSet):
    queryset = HPyloriAntibodySample.objects.all()
    serializer_class = HPyloriAntibodySampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HPyloriAntibodySample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An H. Pylori Antibody Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HPyloriStoolAntigenSampleViewSet(viewsets.ModelViewSet):
    queryset = HPyloriStoolAntigenSample.objects.all()
    serializer_class = HPyloriStoolAntigenSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HPyloriStoolAntigenSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An H. Pylori Stool Antigen Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HBsAgTestSampleViewSet(viewsets.ModelViewSet):
    queryset = HBsAgTestSample.objects.all()
    serializer_class = HBsAgTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HBsAgTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HBsAg Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class HCVAgTestSampleViewSet(viewsets.ModelViewSet):
    queryset = HCVAgTestSample.objects.all()
    serializer_class = HCVAgTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HCVAgTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An HCV Ag Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class RheumatoidFactorSampleViewSet(viewsets.ModelViewSet):
    queryset = RheumatoidFactorSample.objects.all()
    serializer_class = RheumatoidFactorSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if RheumatoidFactorSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Rheumatoid Factor Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class ASOTiterSampleViewSet(viewsets.ModelViewSet):
    queryset = ASOTiterSample.objects.all()
    serializer_class = ASOTiterSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if ASOTiterSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An ASO Titer Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class KHBRapidTestSampleViewSet(viewsets.ModelViewSet):
    queryset = KHBRapidTestSample.objects.all()
    serializer_class = KHBRapidTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if KHBRapidTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A KHB Rapid Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class AFBTestSampleViewSet(viewsets.ModelViewSet):
    queryset = AFBTestSample.objects.all()
    serializer_class = AFBTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if AFBTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("An AFB Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class TBBloodTestSampleViewSet(viewsets.ModelViewSet):
    queryset = TBBloodTestSample.objects.all()
    serializer_class = TBBloodSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if TBBloodTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A TB Blood Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class GramStainTestSampleViewSet(viewsets.ModelViewSet):
    queryset = GramStainTestSample.objects.all()
    serializer_class = GramStainTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if GramStainTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Gram Stain Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class WetMountTestSampleViewSet(viewsets.ModelViewSet):
    queryset = WetMountTestSample.objects.all()
    serializer_class = WetMountTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if WetMountTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Wet Mount Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class HETSampleViewSet(viewsets.ModelViewSet):
    queryset = HETSample.objects.all()
    serializer_class = HETSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if HETSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A HET Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BodyFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = BodyFluidAnalysisSample.objects.all()
    serializer_class = BodyFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BodyFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Body Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CSFAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = CSFAnalysisSample.objects.all()
    serializer_class = CSFAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CSFAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A CSF Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class PeritonealFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = PeritonealFluidAnalysisSample.objects.all()
    serializer_class = PeritonealFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if PeritonealFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Peritoneal Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class SynovialFluidAnalysisSampleViewSet(viewsets.ModelViewSet):
    queryset = SynovialFluidAnalysisSample.objects.all()
    serializer_class = SynovialFluidAnalysisSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if SynovialFluidAnalysisSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Synovial Fluid Analysis Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class BacteriologySampleViewSet(viewsets.ModelViewSet):
    queryset = BacteriologySample.objects.all()
    serializer_class = BacteriologySampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BacteriologySample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Bacteriology Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class KOHPreparationSampleViewSet(viewsets.ModelViewSet):
    queryset = KOHPreparationSample.objects.all()
    serializer_class = KOHPreparationSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if KOHPreparationSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A KOH Preparation Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class CultureTestSampleViewSet(viewsets.ModelViewSet):
    queryset = CultureTestSample.objects.all()
    serializer_class = CultureTestSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if CultureTestSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A Culture Test Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
        
class BFSampleViewSet(viewsets.ModelViewSet):
    queryset = BFSample.objects.all()
    serializer_class = BFSampleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        lab_result_id = self.request.query_params.get('lab_result')
        if lab_result_id:
            queryset = queryset.filter(lab_result_id=lab_result_id)
        return queryset

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        if BFSample.objects.filter(lab_result=lab_result).exists():
            raise serializer.ValidationError("A BF Sample already exists for this LabResult.")
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

class LabResultViewSet(viewsets.ModelViewSet):
    queryset = LabResult.objects.all()
    serializer_class = LabResultSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering logic
        doctor_details_id = self.request.query_params.get('doctor_details')
        if doctor_details_id:
            queryset = queryset.filter(doctor_details_id=doctor_details_id)
            
        uploaded_by_id = self.request.query_params.get('uploaded_by')
        if uploaded_by_id:
            queryset = queryset.filter(uploaded_by_id=uploaded_by_id)
        else:
            try:
                if hasattr(self.request, 'user') and self.request.user and isinstance(self.request.user, Employee):
                    queryset = queryset.filter(uploaded_by=self.request.user)
            except AttributeError:
                pass
                
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(doctor_details__patient_id=patient_id)
        
        # Optimize queries - include all sample types prefetch
        queryset = queryset.select_related(
            'doctor_details',
            'main_category',
            'sub_category',
            'sub_category__tariff',
            'uploaded_by'
        ).prefetch_related(
            Prefetch('cbc_sample', queryset=CBCSample.objects.all()),
            Prefetch('twbc_sample', queryset=TWBCSample.objects.all()),
            Prefetch('hgb_sample', queryset=HGBSample.objects.all()),
            Prefetch('esr_sample', queryset=ESRSample.objects.all()),
            Prefetch('blood_group_sample', queryset=BloodGroupSample.objects.all()),
            Prefetch('stone_exam_sample', queryset=StoneExamSample.objects.all()),
            Prefetch('concentration_sample', queryset=ConcentrationSample.objects.all()),
            Prefetch('occult_blood_sample', queryset=OccultBloodSample.objects.all()),
            Prefetch('physical_test_sample', queryset=PhysicalTestSample.objects.all()),
            Prefetch('chemical_test_sample', queryset=ChemicalTestSample.objects.all()),
            Prefetch('microscopic_test_sample', queryset=MicroscopicTestSample.objects.all()),
            Prefetch('hcg_urine_sample', queryset=HCGUrineSample.objects.all()),
            Prefetch('hcg_serum_sample', queryset=HCGSerumSample.objects.all()),
            Prefetch('fbs_rbs_sample', queryset=FBSRBSSample.objects.all()),
            Prefetch('sgot_ast_sample', queryset=SGOTASTSample.objects.all()),
            Prefetch('sgpt_alt_sample', queryset=SGPTALTSample.objects.all()),
            Prefetch('bilirubin_t_sample', queryset=BilirubinTSample.objects.all()),
            Prefetch('bilirubin_d_sample', queryset=BilirubinDSample.objects.all()),
            Prefetch('alp_sample', queryset=ALPSample.objects.all()),
            Prefetch('creatinine_sample', queryset=CreatinineSample.objects.all()),
            Prefetch('urea_sample', queryset=UreaSample.objects.all()),
            Prefetch('uric_acid_sample', queryset=UricAcidSample.objects.all()),
            Prefetch('lipase_amylase_sample', queryset=LipaseAmylaseSample.objects.all()),
            Prefetch('total_cholesterol_sample', queryset=TotalCholesterolSample.objects.all()),
            Prefetch('triglycerides_sample', queryset=TriglyceridesSample.objects.all()),
            Prefetch('ldlc_sample', queryset=LDLCSample.objects.all()),
            Prefetch('hdlc_sample', queryset=HDLCSample.objects.all()),
            Prefetch('sodium_sample', queryset=SodiumSample.objects.all()),
            Prefetch('potassium_sample', queryset=PotassiumSample.objects.all()),
            Prefetch('calcium_sample', queryset=CalciumSample.objects.all()),
            Prefetch('widal_test_h_sample', queryset=WidalTestHSample.objects.all()),
            Prefetch('widal_test_o_sample', queryset=WidalTestOSample.objects.all()),
            Prefetch('weil_felix_test_sample', queryset=WeilFelixTestSample.objects.all()),
            Prefetch('vdrl_rpr_test_sample', queryset=VDRLRPRTestSample.objects.all()),
            Prefetch('tpha_test_sample', queryset=TPHATestSample.objects.all()),
            Prefetch('h_pylori_antibody_sample', queryset=HPyloriAntibodySample.objects.all()),
            Prefetch('h_pylori_stool_antigen_sample', queryset=HPyloriStoolAntigenSample.objects.all()),
            Prefetch('hbsag_test_sample', queryset=HBsAgTestSample.objects.all()),
            Prefetch('hcv_ag_test_sample', queryset=HCVAgTestSample.objects.all()),
            Prefetch('rheumatoid_factor_sample', queryset=RheumatoidFactorSample.objects.all()),
            Prefetch('aso_titer_sample', queryset=ASOTiterSample.objects.all()),
            Prefetch('khb_rapid_test_sample', queryset=KHBRapidTestSample.objects.all()),
            Prefetch('afb_test_sample', queryset=AFBTestSample.objects.all()),
            Prefetch('tb_blood_test_sample', queryset=TBBloodTestSample.objects.all()),
            Prefetch('gram_stain_test_sample', queryset=GramStainTestSample.objects.all()),
            Prefetch('wet_mount_test_sample', queryset=WetMountTestSample.objects.all()),
            Prefetch('koh_preparation_sample', queryset=KOHPreparationSample.objects.all()),
            Prefetch('culture_test_sample', queryset=CultureTestSample.objects.all()),
            Prefetch('het_sample', queryset=HETSample.objects.all()),
            Prefetch('body_fluid_analysis_sample', queryset=BodyFluidAnalysisSample.objects.all()),
            Prefetch('csf_analysis_sample', queryset=CSFAnalysisSample.objects.all()),
            Prefetch('peritoneal_fluid_analysis_sample', queryset=PeritonealFluidAnalysisSample.objects.all()),
            Prefetch('synovial_fluid_analysis_sample', queryset=SynovialFluidAnalysisSample.objects.all()),
            Prefetch('bacteriology_sample', queryset=BacteriologySample.objects.all()),
            Prefetch('bf_sample', queryset=BFSample.objects.all()),
        )
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()
        lab_result = serializer.instance
        self._create_related_samples(lab_result)

    def perform_update(self, serializer):
        lab_result = serializer.save()
        self._create_related_samples(lab_result)

    def _create_related_samples(self, lab_result):
        """Helper method to create related samples based on sub_category"""
        if not lab_result.sub_category:
            return

        sub_category_name = lab_result.sub_category.name
        sample_creators = {
            "CBC": lambda: CBCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="CBC",
                wbc=0,
                rbc=0,
                hgb=0,
                hct=0,
                mcv=0,
                mch=0,
                mchc=0,
                rdw_cv=0,
                rdw_sd=0,
                plt=0,
                mpv=0,
                pdw=0,
                pct=0,
                p_lcr=0,
                p_lcc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TWBC": lambda: TWBCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="TWBC",
                wbc=0,
                lymph_percent=0,
                lymph_absolute=0,
                gran_percent=0,
                gran_absolute=0,
                mid_percent=0,
                mid_absolute=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HGB": lambda: HGBSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HGB",
                hgb=0,
                rbc=0,
                hct=0,
                mcv=0,
                mch=0,
                mchc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ESR": lambda: ESRSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="ESR",
                esr=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Blood Group": lambda: BloodGroupSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Blood Group",
                blood_group="",
                rh_factor="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Stone Exam": lambda: StoneExamSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Stone Exam",
                stone_type="",
                color="",
                consistency="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Concentration Test": lambda: ConcentrationSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Concentration Test",
                color="",
                appearance="",
                volume=0,
                reaction_ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Occult Blood": lambda: OccultBloodSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Occult Blood",
                occult_blood_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Physical Test": lambda: PhysicalTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Physical Test",
                color="",
                appearance="",
                volume=0,
                reaction_ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Chemical Test": lambda: ChemicalTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Chemical Test",
                protein="",
                glucose="",
                ketone="",
                bilirubin="",
                urobilinogen="",
                blood="",
                nitrite="",
                leukocyte_esterase="",
                ph=0,
                specific_gravity=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Microscopic Test": lambda: MicroscopicTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Microscopic Test",
                rbcs="",
                wbcs="",
                epithelial_cells="",
                casts="",
                crystals="",
                bacteria="",
                yeast="",
                parasites="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCG Urine": lambda: HCGUrineSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HCG Urine",
                hcg_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCG Serum": lambda: HCGSerumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HCG Serum",
                hcg_level=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "FBS/RBS": lambda: FBSRBSSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="FBS/RBS",
                test_type="",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "SGOT/AST": lambda: SGOTASTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="SGOT/AST",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "SGPT/ALT": lambda: SGPTALTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="SGPT/ALT",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bilirubin Total": lambda: BilirubinTSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Bilirubin Total",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bilirubin Direct": lambda: BilirubinDSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Bilirubin Direct",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ALP": lambda: ALPSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="ALP",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Creatinine": lambda: CreatinineSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Creatinine",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Urea": lambda: UreaSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Urea",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Uric Acid": lambda: UricAcidSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Uric Acid",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Lipase/Amylase": lambda: LipaseAmylaseSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Lipase/Amylase",
                lipase_result=0,
                lipase_reference="",
                amylase_result=0,
                amylase_reference="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Total Cholesterol": lambda: TotalCholesterolSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Total Cholesterol",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Triglycerides": lambda: TriglyceridesSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Triglycerides",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "LDL-C": lambda: LDLCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="LDL-C",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HDL-C": lambda: HDLCSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HDL-C",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Sodium": lambda: SodiumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Sodium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Potassium": lambda: PotassiumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Potassium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Calcium": lambda: CalciumSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="Calcium",
                result=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Widal Test H": lambda: WidalTestHSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Widal Test H",
                widal_h_antigen_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Widal Test O": lambda: WidalTestOSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Widal Test O",
                widal_o_antigen_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Weil Felix Test": lambda: WeilFelixTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Weil Felix Test",
                antigen_ox19_titer="",
                antigen_ox2_titer="",
                antigen_oxk_titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "VDRL/RPR Test": lambda: VDRLRPRTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="VDRL/RPR Test",
                test_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TPHA Test": lambda: TPHATestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="TPHA Test",
                tpha_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "H. Pylori Antibody": lambda: HPyloriAntibodySample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="H. Pylori Antibody",
                antibody_result="",
                titer="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "H. Pylori Stool Antigen": lambda: HPyloriStoolAntigenSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="H. Pylori Stool Antigen",
                stool_antigen_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HBsAg Test": lambda: HBsAgTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="HBsAg Test",
                hbsag_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HCVAg Test": lambda: HCVAgTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="HCVAg Test",
                hcvag_result="",
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Rheumatoid Factor": lambda: RheumatoidFactorSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Rheumatoid Factor",
                rf_result="",
                rf_value=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "ASO Titer": lambda: ASOTiterSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="ASO Titer",
                aso_titer=0,
                reference_range="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "KHB Rapid Test": lambda: KHBRapidTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="KHB Rapid Test",
                rapid_test_result="",
                test_type="",
                method_used="",
                reference_range="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "AFB Test": lambda: AFBTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="AFB Test",
                spot_sample_result="",
                morning_sample_result="",
                second_spot_sample_result="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "TB Blood Test": lambda: TBBloodTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="TB Blood Test",
                tb_blood_test_result="",
                method_used="",
                reference_range="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Gram Stain Test": lambda: GramStainTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Gram Stain Test",
                sample_type="",
                organism_type="",
                cellular_elements="",
                background="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Wet Mount Test": lambda: WetMountTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Wet Mount Test",
                sample_type="",
                organisms_observed="",
                motility="",
                pus_cells="",
                rbcs="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "KOH Preparation": lambda: KOHPreparationSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="KOH Preparation",
                sample_type="",
                fungal_elements="",
                yeast_cells="",
                pseudohyphae="",
                background="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Culture Test": lambda: CultureTestSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Culture Test",
                sample_type="",
                organism_isolated="",
                growth_description="",
                antibiotic_sensitivity="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "HET": lambda: HETSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="HET",
                het=0,
                hgb=0,
                rbc=0,
                mcv=0,
                mch=0,
                mchc=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Body Fluid Analysis": lambda: BodyFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Body Fluid Analysis",
                fluid_type="",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "CSF Analysis": lambda: CSFAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="CSF Analysis",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                chloride=0,
                opening_pressure=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Peritoneal Fluid Analysis": lambda: PeritonealFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Peritoneal Fluid Analysis",
                appearance="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                ldh=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Synovial Fluid Analysis": lambda: SynovialFluidAnalysisSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Synovial Fluid Analysis",
                appearance="",
                viscosity="",
                rbc_count=0,
                wbc_count=0,
                neutrophils=0,
                lymphocytes=0,
                glucose=0,
                protein=0,
                crystals="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "Bacteriology": lambda: BacteriologySample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                patient_name="Bacteriology",
                sample_type="",
                culture_result="",
                colony_count="",
                antibiotic_sensitivity_pattern="",
                method_used="",
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
            "BF": lambda: BFSample.objects.create(
                lab_result=lab_result,
                sampleid="default",
                name="BF",
                parasite_seen=None,
                parasite_species="",
                parasite_stage="",
                parasite_density=0,
                additional_note="" if lab_result.result_type == "text" else None,
                image=None if lab_result.result_type == "image" else None
            ),
        }

        creator = sample_creators.get(sub_category_name)
        if creator and not hasattr(lab_result, f"{sub_category_name.lower().replace(' ', '_')}_sample"):
            creator()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if not serializer.validated_data.get('uploaded_by') and hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['uploaded_by'] = request.user
            else:
                if 'uploaded_by' not in serializer.validated_data:
                    return Response({"error": "uploaded_by is required if user is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"error": "Invalid request object"}, status=status.HTTP_400_BAD_REQUEST)
        doctor_details_id = serializer.validated_data['doctor_details']
        doctor_details = get_object_or_404(DoctorDetails, id=doctor_details_id.id)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InjectionRoom, DoctorDetails, Employee
from .serializers import InjectionRoomSerializer
from django.db.models import Sum, Count
from django.utils.timezone import now
import calendar

class InjectionRoomViewSet(viewsets.ModelViewSet):
    queryset = InjectionRoom.objects.all()
    serializer_class = InjectionRoomSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor_details', 'nurse', 'doctor_details__patient']  # nested lookups allowed
    search_fields = ['doctor_details__patient__first_name', 'doctor_details__patient__last_name', 'nurse__first_name']
    ordering_fields = ['id']  
    ordering = ['-id']


    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(doctor_details__patient=patient_id)
        doctor_details_id = self.request.query_params.get('doctor_details')
        if doctor_details_id:
            queryset = queryset.filter(doctor_details_id=doctor_details_id)
        nurse_id = self.request.query_params.get('nurse')
        if nurse_id:
            queryset = queryset.filter(nurse_id=nurse_id)
        if hasattr(self.request.user, 'id') and isinstance(self.request.user, Employee):
            queryset = queryset.filter(doctor_details__referral_type__in=['injection_only', 'both'])
        queryset = queryset.select_related(
            'doctor_details',
            'doctor_details__doctor',
            'nurse'
        ).prefetch_related('doctor_details__patient')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor_details_id = serializer.validated_data.get('doctor_details')
        doctor_details = get_object_or_404(DoctorDetails, id=doctor_details_id.id)
        if doctor_details.referral_type not in ['injection_only', 'both']:
            return Response(
                {"error": "This visit has not been referred to the injection room"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        appointed_by_id = self.request.query_params.get('appointed_by')
        if appointed_by_id:
            queryset = queryset.filter(appointed_by_id=appointed_by_id)
        queryset = queryset.select_related('patient', 'appointed_by')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
            serializer.validated_data['appointed_by'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
            serializer.validated_data['appointed_by'] = request.user
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'receptionist']
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__phone_number',
        'receptionist_name',
    ]
    ordering_fields = ['id', 'payment_amount', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        return super().get_queryset().select_related('patient', 'receptionist')

    def filter_custom_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    # ------------------ REPORT ENDPOINTS WITH PAGINATION ------------------

    @action(detail=False, methods=['get'])
    def all_payments(self, request):
        queryset = self.filter_custom_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        totals = queryset.aggregate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def today_payment(self, request):
        today = now().date()
        queryset = self.filter_custom_queryset(
            self.get_queryset().filter(created_at__date=today)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        totals = queryset.aggregate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "date": str(today),
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "date": str(today),
            "totals": totals,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def weekly_payment(self, request):
        today = now().date()
        start_week = today - timedelta(days=today.weekday())  # Monday
        end_week = start_week + timedelta(days=6)  # Sunday

        queryset = self.get_queryset().filter(created_at__date__range=[start_week, end_week])

        # Filter by weekday if requested
        weekday = request.query_params.get("day")  # e.g. Monday, Tuesday
        if weekday:
            weekday_map = {
                "sunday": 1, "monday": 2, "tuesday": 3,
                "wednesday": 4, "thursday": 5, "friday": 6, "saturday": 7
            }
            day_num = weekday_map.get(weekday.lower())
            if day_num:
                queryset = queryset.filter(created_at__week_day=day_num)

        queryset = self.filter_custom_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        breakdown = queryset.values("created_at__week_day") \
                            .annotate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        day_map = {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
                   5: "Thursday", 6: "Friday", 7: "Saturday"}
        breakdown_list = [
            {"day": day_map[item["created_at__week_day"]],
             "total_amount": item["total_amount"] or 0,
             "total_count": item["total_count"]}
            for item in breakdown
        ]

        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "week_start": str(start_week),
            "week_end": str(end_week),
            "breakdown": breakdown_list,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "week_start": str(start_week),
            "week_end": str(end_week),
            "breakdown": breakdown_list,
            "per_patient": list(per_patient),
            "data": data
        })

    @action(detail=False, methods=['get'])
    def monthly_payment(self, request):
        year = now().year
        queryset = self.get_queryset().filter(created_at__year=year)

        month = request.query_params.get("month")  # e.g. September, 9
        if month:
            try:
                if month.isdigit():
                    month_num = int(month)
                else:
                    month_num = list(calendar.month_name).index(month.capitalize())
                queryset = queryset.filter(created_at__month=month_num)
            except Exception:
                pass

        queryset = self.filter_custom_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        breakdown = queryset.values("created_at__month") \
                            .annotate(total_amount=Sum("payment_amount"), total_count=Count("id"))
        results = [
            {"month": calendar.month_name[item["created_at__month"]],
             "total_amount": item["total_amount"] or 0,
             "total_count": item["total_count"]}
            for item in breakdown
        ]

        per_patient = queryset.values("patient__id", "patient__first_name", "patient__last_name") \
                              .annotate(patient_total=Sum("payment_amount"), payment_count=Count("id"))

        return self.get_paginated_response({
            "year": year,
            "breakdown": results,
            "per_patient": list(per_patient),
            "data": data
        }) if page is not None else Response({
            "year": year,
            "breakdown": results,
            "per_patient": list(per_patient),
            "data": data
        })

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['receptionist'] = request.user
            else:
                if 'receptionist' not in serializer.validated_data:
                    return Response({"error": "receptionist is required if user is not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"error": "Invalid request object"}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)

        instance = serializer.instance
        instance = Payment.objects.select_related("patient", "receptionist").get(pk=instance.pk)
        output_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            if hasattr(request, 'user') and request.user and isinstance(request.user, Employee):
                serializer.validated_data['receptionist'] = request.user
        except AttributeError:
            pass
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('subcategories')
        return queryset

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        main_category_id = self.request.query_params.get('main_category')
        if main_category_id:
            queryset = queryset.filter(main_category_id=main_category_id)
        queryset = queryset.select_related('main_category', 'tariff')
        return queryset

class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        queryset = queryset.select_related('category')
        return queryset

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer
    pagination_class = None
    filter_backends = []

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        doctor_id = self.request.query_params.get('doctor')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        queryset = queryset.select_related('patient', 'doctor')
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee) and request.user.role == 'Doctor':
            serializer.validated_data['doctor'] = request.user
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if hasattr(request.user, 'id') and isinstance(request.user, Employee) and request.user.role == 'Doctor':
            serializer.validated_data['doctor'] = request.user
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
class MedicationPriceViewSet(viewsets.ModelViewSet):
    queryset = MedicationPrice.objects.all()
    serializer_class = MedicationPriceSerializer

    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        queryset = super().get_queryset()
        tariff_id = self.request.query_params.get('tariff')
        if tariff_id:
            queryset = queryset.filter(tariff_id=tariff_id)
        queryset = queryset.select_related('tariff')
        return queryset

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    pagination_class = None
    filter_backends = []
