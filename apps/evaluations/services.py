from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.evaluations.models import (
    EvaluationSubmission,
    EvaluationResponse,
    EvaluationCriteria,
)
from apps.sync.models import StudentCourseEnrollment, StudentSync


class EvaluationSubmissionService:
    @staticmethod
    @transaction.atomic
    def submit_evaluation(*, student_user, campaign, course, responses_data):
        if student_user.role != "STUDENT":
            raise ValidationError("Seuls les étudiants peuvent soumettre une évaluation.")

        if not student_user.student_profile:
            raise ValidationError("Compte étudiant invalide.")

        student_profile: StudentSync = student_user.student_profile

        if not campaign.is_open:
            raise ValidationError("La campagne n'est pas ouverte.")

        enrollment_exists = StudentCourseEnrollment.objects.filter(
            student=student_profile,
            course=course,
            semester=campaign.semester,
            is_active=True,
        ).exists()

        if not enrollment_exists:
            raise ValidationError("L'étudiant n'est pas inscrit à ce cours.")

        already_submitted = EvaluationSubmission.objects.filter(
            campaign=campaign,
            course=course,
            student=student_user,
        ).exists()

        if already_submitted:
            raise ValidationError("Vous avez déjà soumis cette évaluation.")

        active_criteria = EvaluationCriteria.objects.filter(is_active=True)

        active_criteria_ids = {str(criteria.id) for criteria in active_criteria}
        submitted_criteria_ids = {str(item["criteria"].id) for item in responses_data}

        if active_criteria_ids != submitted_criteria_ids:
            raise ValidationError("Tous les critères actifs doivent être évalués.")

        total_weight = Decimal("0")
        weighted_score = Decimal("0")

        for item in responses_data:
            criteria = item["criteria"]
            score = Decimal(str(item["score"]))

            total_weight += criteria.weight
            weighted_score += (score / Decimal("5")) * criteria.weight

        if total_weight == 0:
            raise ValidationError("Poids total invalide.")

        global_score = (weighted_score / total_weight) * Decimal("100")

        submission = EvaluationSubmission.objects.create(
            campaign=campaign,
            course=course,
            student=student_user,
            status=EvaluationSubmission.Status.SUBMITTED,
            global_score=round(global_score, 2),
            submitted_at=timezone.now(),
        )

        responses = [
            EvaluationResponse(
                submission=submission,
                criteria=item["criteria"],
                score=item["score"],
                comment=item.get("comment"),
            )
            for item in responses_data
        ]

        EvaluationResponse.objects.bulk_create(responses)

        return submission