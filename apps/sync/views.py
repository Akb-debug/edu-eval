from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny

from .models import (
    Department,
    AcademicSemester,
    TeacherSync,
    StudentSync,
    CourseSync,
    StudentCourseEnrollment,
    SyncLog,
)

from .serializers import (
    DepartmentSerializer,
    AcademicSemesterSerializer,
    TeacherSyncSerializer,
    StudentSyncSerializer,
    CourseSyncSerializer,
    StudentCourseEnrollmentSerializer,
    SyncLogSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    #permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["name"]


class AcademicSemesterViewSet(viewsets.ModelViewSet):
    queryset = AcademicSemester.objects.all()
    serializer_class = AcademicSemesterSerializer
   # permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "academic_year"]
    ordering_fields = ["start_date", "end_date", "name"]
    ordering = ["-start_date"]


class TeacherSyncViewSet(viewsets.ModelViewSet):
    queryset = TeacherSync.objects.select_related("department").all()
    serializer_class = TeacherSyncSerializer
    #permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "university_id",
        "matricule",
        "first_name",
        "last_name",
        "email",
        "department__name",
        "grade",
        "specialty",
    ]
    ordering_fields = ["last_name", "first_name", "email", "created_at"]
    ordering = ["last_name", "first_name"]


class StudentSyncViewSet(viewsets.ModelViewSet):
    queryset = StudentSync.objects.select_related("department").all()
    serializer_class = StudentSyncSerializer
    #permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "university_id",
        "student_code",
        "first_name",
        "last_name",
        "email",
        "department__name",
        "level",
        "cohort",
    ]
    ordering_fields = ["last_name", "first_name", "student_code", "created_at"]
    ordering = ["last_name", "first_name"]


class CourseSyncViewSet(viewsets.ModelViewSet):
    queryset = CourseSync.objects.select_related(
        "teacher",
        "department",
        "semester",
    ).all()
    serializer_class = CourseSyncSerializer
    #permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "university_id",
        "code",
        "name",
        "teacher__first_name",
        "teacher__last_name",
        "department__name",
        "semester__name",
        "level",
        "cohort",
    ]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["code"]


class StudentCourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentCourseEnrollment.objects.select_related(
        "student",
        "course",
        "semester",
        "course__teacher",
    ).all()
    serializer_class = StudentCourseEnrollmentSerializer
    permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "student__student_code",
        "student__first_name",
        "student__last_name",
        "course__code",
        "course__name",
        "semester__name",
    ]
    ordering_fields = ["enrolled_at", "synced_at"]
    ordering = ["-enrolled_at"]


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    #permission_classes = [AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["sync_type", "status", "message"]
    ordering_fields = ["started_at", "ended_at"]
    ordering = ["-started_at"]