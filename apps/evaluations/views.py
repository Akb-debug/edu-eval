from rest_framework import filters, viewsets

from apps.authentication.permissions import IsAdminOrDirector
from .models import EvaluationCriteria
from .serializers import EvaluationCriteriaSerializer

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.evaluations.services import EvaluationSubmissionService
from .models import EvaluationSubmission
from .serializers import (
    EvaluationCriteriaSerializer,
    EvaluationSubmissionCreateSerializer,
    EvaluationSubmissionSerializer,
)

from rest_framework.views import APIView

from apps.campaigns.models import EvaluationCampaign
from apps.sync.models import StudentCourseEnrollment
from .serializers import MyEvaluableCourseSerializer



class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer
    #permission_classes = [IsAdminOrDirector]
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "name",
        "description",
        "category",
    ]
    ordering_fields = [
        "name",
        "category",
        "weight",
        "created_at",
    ]
    ordering = ["category", "name"]

    def get_permissions(self):
        # Lecture pour tous, écriture pour admin seulement
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrDirector()]
        return [IsAuthenticated()]

class EvaluationSubmissionViewSet(viewsets.ModelViewSet):
    queryset = EvaluationSubmission.objects.select_related(
        "campaign",
        "course",
        "course__teacher",
        "student",
    ).prefetch_related("responses", "responses__criteria")

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return EvaluationSubmissionCreateSerializer
        return EvaluationSubmissionSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in ["ADMIN", "DIRECTOR"]:
            return self.queryset

        if user.role == "STUDENT":
            return self.queryset.filter(student=user)

        if user.role == "TEACHER" and user.teacher_profile:
            return self.queryset.filter(course__teacher=user.teacher_profile)

        return self.queryset.none()

    def create(self, request, *args, **kwargs):
        serializer = EvaluationSubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            submission = EvaluationSubmissionService.submit_evaluation(
                student_user=request.user,
                campaign=serializer.validated_data["campaign_id"],
                course=serializer.validated_data["course_id"],
                responses_data=serializer.validated_data["responses"],
            )
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            EvaluationSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )

class MyEvaluableCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "STUDENT" or not user.student_profile:
            return Response(
                {"detail": "Seuls les étudiants peuvent accéder à cette ressource."},
                status=status.HTTP_403_FORBIDDEN,
            )

        active_campaigns = EvaluationCampaign.objects.filter(
            status=EvaluationCampaign.Status.ACTIVE
        )

        enrollments = StudentCourseEnrollment.objects.select_related(
            "course",
            "course__teacher",
            "semester",
        ).filter(
            student=user.student_profile,
            is_active=True,
            semester__in=active_campaigns.values("semester"),
        )

        data = []

        for enrollment in enrollments:
            campaign = active_campaigns.filter(
                semester=enrollment.semester
            ).first()

            if not campaign or not campaign.is_open:
                continue

            already_submitted = EvaluationSubmission.objects.filter(
                campaign=campaign,
                course=enrollment.course,
                student=user,
            ).exists()

            data.append({
                "course_id": enrollment.course.id,
                "course_code": enrollment.course.code,
                "course_name": enrollment.course.name,
                "teacher_name": enrollment.course.teacher.full_name,
                "semester_id": enrollment.semester.id,
                "semester_name": enrollment.semester.name,
                "campaign_id": campaign.id,
                "campaign_title": campaign.title,
                "already_submitted": already_submitted,
            })

        serializer = MyEvaluableCourseSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)