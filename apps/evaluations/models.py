from django.db import models

# Create your models here.
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from django.conf import settings
from apps.campaigns.models import EvaluationCampaign
from apps.sync.models import CourseSync


class EvaluationCriteria(models.Model):
    class Category(models.TextChoices):
        PEDAGOGY = "PEDAGOGY", "Pédagogie"
        CONTENT = "CONTENT", "Contenu du cours"
        BEHAVIOR = "BEHAVIOR", "Comportement"
        AVAILABILITY = "AVAILABILITY", "Disponibilité"
        ORGANIZATION = "ORGANIZATION", "Organisation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=30, choices=Category.choices)

    weight = models.DecimalField(max_digits=5, decimal_places=2)

    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "evaluations_criteria"
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self):
        if self.weight <= 0:
            raise ValidationError("Le poids du critère doit être supérieur à 0.")

        if self.weight > 100:
            raise ValidationError("Le poids du critère ne peut pas dépasser 100.")

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.weight}%)"
    

class EvaluationSubmission(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Brouillon"
        SUBMITTED = "SUBMITTED", "Soumise"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    campaign = models.ForeignKey(
        EvaluationCampaign,
        on_delete=models.PROTECT,
        related_name="submissions",
    )

    course = models.ForeignKey(
        CourseSync,
        on_delete=models.PROTECT,
        related_name="evaluation_submissions",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evaluation_submissions",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    global_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    submitted_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "evaluations_submissions"
        unique_together = ("campaign", "course", "student")
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["campaign"]),
            models.Index(fields=["course"]),
            models.Index(fields=["student"]),
            models.Index(fields=["status"]),
        ]

    def clean(self):
        if self.student and self.student.role != "STUDENT":
            raise ValidationError("Seul un étudiant peut soumettre une évaluation.")

        if self.campaign and not self.campaign.is_open:
            raise ValidationError("La campagne n’est pas ouverte aux évaluations.")

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.email} - {self.course.code} - {self.campaign.title}"


class EvaluationResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(
        EvaluationSubmission,
        on_delete=models.CASCADE,
        related_name="responses",
    )

    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.PROTECT,
        related_name="responses",
    )

    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "evaluations_responses"
        unique_together = ("submission", "criteria")
        ordering = ["criteria__category", "criteria__name"]
        indexes = [
            models.Index(fields=["submission"]),
            models.Index(fields=["criteria"]),
        ]

    def clean(self):
        if self.score < 1 or self.score > 5:
            raise ValidationError("Le score doit être compris entre 1 et 5.")

    def __str__(self):
        return f"{self.criteria.name} = {self.score}/5"