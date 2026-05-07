from rest_framework.routers import DefaultRouter

from .views import (
    DepartmentViewSet,
    AcademicSemesterViewSet,
    TeacherSyncViewSet,
    StudentSyncViewSet,
    CourseSyncViewSet,
    StudentCourseEnrollmentViewSet,
    SyncLogViewSet,
)

router = DefaultRouter()

router.register(r"departments", DepartmentViewSet, basename="departments")
router.register(r"semesters", AcademicSemesterViewSet, basename="semesters")
router.register(r"teachers", TeacherSyncViewSet, basename="teachers")
router.register(r"students", StudentSyncViewSet, basename="students")
router.register(r"courses", CourseSyncViewSet, basename="courses")
router.register(r"enrollments", StudentCourseEnrollmentViewSet, basename="enrollments")
router.register(r"logs", SyncLogViewSet, basename="sync-logs")

urlpatterns = router.urls