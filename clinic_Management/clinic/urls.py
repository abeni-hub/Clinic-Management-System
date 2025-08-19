from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import logout_view
from .views import (
    EmployeeRegistrationView,
    LoginView,
    TokenRefreshView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    RoleViewSet,
    EmployeeViewSet,
    PatientViewSet,
    PatientNurseDetailsViewSet,
    DoctorViewSet,
    DoctorDetailsViewSet,
    LabResultViewSet,
    InjectionRoomViewSet,
    DepartmentViewSet,
    AppointmentViewSet,
    PaymentViewSet,
    CategoryViewSet,
    SubCategoryViewSet,
    LabTestViewSet,
    TariffViewSet,
    MedicationViewSet,
    CBCSampleViewSet,
    TWBCSampleViewSet,
    HGBSampleViewSet,
    ESRSampleViewSet,
    BloodGroupSampleViewSet,
    StoneExamSampleViewSet,
    ConcentrationSampleViewSet,
    OccultBloodSampleViewSet,
    PhysicalTestSampleViewSet,
    ChemicalTestSampleViewSet,
    MicroscopicTestSampleViewSet,
    HCGUrineSampleViewSet,
    HCGSerumSampleViewSet,
    FBSRBSSampleViewSet,
    SGOTASTSampleViewSet,
    SGPTALTSampleViewSet,
    BilirubinTSampleViewSet,
    BilirubinDSampleViewSet,
    ALPSampleViewSet,
    CreatinineSampleViewSet,
    UreaSampleViewSet,
    UricAcidSampleViewSet,
    LipaseAmylaseSampleViewSet,
    TotalCholesterolSampleViewSet,
    TriglyceridesSampleViewSet,
    LDLCSampleViewSet,
    HDLCSampleViewSet,
    SodiumSampleViewSet,
    PotassiumSampleViewSet,
    CalciumSampleViewSet,
    WidalTestHSampleViewSet,
    WidalTestOSampleViewSet,
    WeilFelixTestSampleViewSet,
    VDRLRPRTestSampleViewSet,
    TPHATestSampleViewSet,
    HPyloriAntibodySampleViewSet,
    HPyloriStoolAntigenSampleViewSet,
    HBsAgTestSampleViewSet,
    HCVAgTestSampleViewSet,
    RheumatoidFactorSampleViewSet,
    ASOTiterSampleViewSet,
    KHBRapidTestSampleViewSet,
    AFBTestSampleViewSet,
    TBBloodTestSampleViewSet,
    GramStainTestSampleViewSet,
    WetMountTestSampleViewSet,
    KOHPreparationSampleViewSet,
    CultureTestSampleViewSet,
    HETSampleViewSet,
    BodyFluidAnalysisSampleViewSet,
    CSFAnalysisSampleViewSet,
    PeritonealFluidAnalysisSampleViewSet,
    SynovialFluidAnalysisSampleViewSet,
    BacteriologySampleViewSet,
    MedicationPriceViewSet,
    MaterialViewSet,
    BFSampleViewSet
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'patient-nurse', PatientNurseDetailsViewSet, basename='patient-nurse-details')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'doctor-details', DoctorDetailsViewSet, basename='doctor-details')
router.register(r'lab-results', LabResultViewSet, basename='lab-results')
router.register(r'injection-room', InjectionRoomViewSet, basename='injection-room')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'subcategories', SubCategoryViewSet, basename='subcategory')
router.register(r'lab-tests', LabTestViewSet, basename='lab-test')
router.register(r'tariffs', TariffViewSet, basename='tariff')
router.register(r'medications', MedicationViewSet, basename='medication')
router.register(r'medication-prices', MedicationPriceViewSet, basename='medication-price')
router.register(r'materials', MaterialViewSet, basename='material')

# Sample endpoints
router.register(r'cbc-samples', CBCSampleViewSet, basename='cbc-sample')
router.register(r'twbc-samples', TWBCSampleViewSet, basename='twbc-sample')
router.register(r'hgb-samples', HGBSampleViewSet, basename='hgb-sample')
router.register(r'esr-samples', ESRSampleViewSet, basename='esr-sample')
router.register(r'blood-group-samples', BloodGroupSampleViewSet, basename='blood-group-sample')
router.register(r'stone-exam-samples', StoneExamSampleViewSet, basename='stone-exam-sample')
router.register(r'concentration-samples', ConcentrationSampleViewSet, basename='concentration-sample')
router.register(r'occult-blood-samples', OccultBloodSampleViewSet, basename='occult-blood-sample')
router.register(r'physical-test-samples', PhysicalTestSampleViewSet, basename='physical-test-sample')
router.register(r'chemical-test-samples', ChemicalTestSampleViewSet, basename='chemical-test-sample')
router.register(r'microscopic-test-samples', MicroscopicTestSampleViewSet, basename='microscopic-test-sample')
router.register(r'hcg-urine-samples', HCGUrineSampleViewSet, basename='hcg-urine-sample')
router.register(r'hcg-serum-samples', HCGSerumSampleViewSet, basename='hcg-serum-sample')
router.register(r'fbs-rbs-samples', FBSRBSSampleViewSet, basename='fbs-rbs-sample')
router.register(r'sgot-ast-samples', SGOTASTSampleViewSet, basename='sgot-ast-sample')
router.register(r'sgpt-alt-samples', SGPTALTSampleViewSet, basename='sgpt-alt-sample')
router.register(r'bilirubin-t-samples', BilirubinTSampleViewSet, basename='bilirubin-t-sample')
router.register(r'bilirubin-d-samples', BilirubinDSampleViewSet, basename='bilirubin-d-sample')
router.register(r'alp-samples', ALPSampleViewSet, basename='alp-sample')
router.register(r'creatinine-samples', CreatinineSampleViewSet, basename='creatinine-sample')
router.register(r'urea-samples', UreaSampleViewSet, basename='urea-sample')
router.register(r'uric-acid-samples', UricAcidSampleViewSet, basename='uric-acid-sample')
router.register(r'lipase-amylase-samples', LipaseAmylaseSampleViewSet, basename='lipase-amylase-sample')
router.register(r'total-cholesterol-samples', TotalCholesterolSampleViewSet, basename='total-cholesterol-sample')
router.register(r'triglycerides-samples', TriglyceridesSampleViewSet, basename='triglycerides-sample')
router.register(r'ldlc-samples', LDLCSampleViewSet, basename='ldlc-sample')
router.register(r'hdlc-samples', HDLCSampleViewSet, basename='hdlc-sample')
router.register(r'sodium-samples', SodiumSampleViewSet, basename='sodium-sample')
router.register(r'potassium-samples', PotassiumSampleViewSet, basename='potassium-sample')
router.register(r'calcium-samples', CalciumSampleViewSet, basename='calcium-sample')
router.register(r'widal-test-h-samples', WidalTestHSampleViewSet, basename='widal-test-h-sample')
router.register(r'widal-test-o-samples', WidalTestOSampleViewSet, basename='widal-test-o-sample')
router.register(r'weil-felix-test-samples', WeilFelixTestSampleViewSet, basename='weil-felix-test-sample')
router.register(r'vdrl-rpr-test-samples', VDRLRPRTestSampleViewSet, basename='vdrl-rpr-test-sample')
router.register(r'tpha-test-samples', TPHATestSampleViewSet, basename='tpha-test-sample')
router.register(r'h-pylori-antibody-samples', HPyloriAntibodySampleViewSet, basename='h-pylori-antibody-sample')
router.register(r'h-pylori-stool-antigen-samples', HPyloriStoolAntigenSampleViewSet, basename='h-pylori-stool-antigen-sample')
router.register(r'hbsag-test-samples', HBsAgTestSampleViewSet, basename='hbsag-test-sample')
router.register(r'hcv-ag-test-samples', HCVAgTestSampleViewSet, basename='hcv-ag-test-sample')
router.register(r'rheumatoid-factor-samples', RheumatoidFactorSampleViewSet, basename='rheumatoid-factor-sample')
router.register(r'aso-titer-samples', ASOTiterSampleViewSet, basename='aso-titer-sample')
router.register(r'khb-rapid-test-samples', KHBRapidTestSampleViewSet, basename='khb-rapid-test-sample')
router.register(r'afb-test-samples', AFBTestSampleViewSet, basename='afb-test-sample')
router.register(r'tb-blood-test-samples', TBBloodTestSampleViewSet, basename='tb-blood-test-sample')
router.register(r'gram-stain-test-samples', GramStainTestSampleViewSet, basename='gram-stain-test-sample')
router.register(r'wet-mount-test-samples', WetMountTestSampleViewSet, basename='wet-mount-test-sample')
router.register(r'koh-preparation-samples', KOHPreparationSampleViewSet, basename='koh-preparation-sample')
router.register(r'culture-test-samples', CultureTestSampleViewSet, basename='culture-test-sample')
router.register(r'het-samples', HETSampleViewSet, basename='het-sample')
router.register(r'body-fluid-analysis-samples', BodyFluidAnalysisSampleViewSet, basename='body-fluid-analysis-sample')
router.register(r'csf-analysis-samples', CSFAnalysisSampleViewSet, basename='csf-analysis-sample')
router.register(r'peritoneal-fluid-analysis-samples', PeritonealFluidAnalysisSampleViewSet, basename='peritoneal-fluid-analysis-sample')
router.register(r'synovial-fluid-analysis-samples', SynovialFluidAnalysisSampleViewSet, basename='synovial-fluid-analysis-sample')
router.register(r'bacteriology-samples', BacteriologySampleViewSet, basename='bacteriology-sample')
router.register(r'bf-samples', BFSampleViewSet, basename='bf-sample')

urlpatterns = [
    path('register/', EmployeeRegistrationView.as_view(), name='employee-register'),
    path('login/', LoginView.as_view(), name='employee-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', logout_view, name='logout'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('', include(router.urls)),
]
