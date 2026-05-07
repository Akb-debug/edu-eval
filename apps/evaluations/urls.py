from rest_framework.routers import DefaultRouter

from .views import EvaluationCriteriaViewSet, EvaluationSubmissionViewSet

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    EvaluationCriteriaViewSet,
    EvaluationSubmissionViewSet,
    MyEvaluableCoursesAPIView,
)

router = DefaultRouter()
router.register(r"criteria", EvaluationCriteriaViewSet, basename="evaluation-criteria")
router.register(r"submissions", EvaluationSubmissionViewSet, basename="evaluation-submissions")

urlpatterns = [
    path("my-courses/", MyEvaluableCoursesAPIView.as_view(), name="my-evaluable-courses"),
]

urlpatterns += router.urls