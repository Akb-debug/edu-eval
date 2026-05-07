from decimal import Decimal

from rest_framework import serializers

from .models import EvaluationCriteria

from apps.campaigns.models import EvaluationCampaign
from apps.sync.models import CourseSync
from .models import EvaluationSubmission, EvaluationResponse


class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriteria
        fields = [
            "id",
            "name",
            "description",
            "category",
            "weight",
            "is_active",
            "version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_weight(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Le poids doit être supérieur à 0.")

        if value > Decimal("100"):
            raise serializers.ValidationError("Le poids ne peut pas dépasser 100.")

        return value


class EvaluationResponseInputSerializer(serializers.Serializer):
    criteria_id = serializers.UUIDField()
    score = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_criteria_id(self, value):
        try:
            return EvaluationCriteria.objects.get(id=value, is_active=True)
        except EvaluationCriteria.DoesNotExist:
            raise serializers.ValidationError("Critère introuvable ou inactif.")


class EvaluationSubmissionCreateSerializer(serializers.Serializer):
    campaign_id = serializers.UUIDField()
    course_id = serializers.UUIDField()
    responses = EvaluationResponseInputSerializer(many=True)

    def validate_campaign_id(self, value):
        try:
            return EvaluationCampaign.objects.get(id=value)
        except EvaluationCampaign.DoesNotExist:
            raise serializers.ValidationError("Campagne introuvable.")

    def validate_course_id(self, value):
        try:
            return CourseSync.objects.get(id=value, is_active=True)
        except CourseSync.DoesNotExist:
            raise serializers.ValidationError("Cours introuvable ou inactif.")

    def validate(self, attrs):
        if not attrs.get("responses"):
            raise serializers.ValidationError({
                "responses": "La liste des réponses ne peut pas être vide."
            })

        criteria_ids = [str(item["criteria_id"].id) for item in attrs["responses"]]

        if len(criteria_ids) != len(set(criteria_ids)):
            raise serializers.ValidationError({
                "responses": "Un critère ne peut pas être évalué plusieurs fois."
            })

        return attrs


class EvaluationResponseSerializer(serializers.ModelSerializer):
    criteria_name = serializers.CharField(source="criteria.name", read_only=True)
    criteria_category = serializers.CharField(source="criteria.category", read_only=True)

    class Meta:
        model = EvaluationResponse
        fields = [
            "id",
            "criteria",
            "criteria_name",
            "criteria_category",
            "score",
            "comment",
            "created_at",
        ]


class EvaluationSubmissionSerializer(serializers.ModelSerializer):
    campaign_title = serializers.CharField(source="campaign.title", read_only=True)
    course_name = serializers.CharField(source="course.name", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)
    teacher_name = serializers.CharField(source="course.teacher.full_name", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)
    responses = EvaluationResponseSerializer(many=True, read_only=True)

    class Meta:
        model = EvaluationSubmission
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "course",
            "course_name",
            "course_code",
            "teacher_name",
            "student",
            "student_email",
            "status",
            "global_score",
            "submitted_at",
            "created_at",
            "updated_at",
            "responses",
        ]
        read_only_fields = fields


class MyEvaluableCourseSerializer(serializers.Serializer):
    course_id = serializers.UUIDField()
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    teacher_name = serializers.CharField()
    semester_id = serializers.UUIDField()
    semester_name = serializers.CharField()
    campaign_id = serializers.UUIDField()
    campaign_title = serializers.CharField()
    already_submitted = serializers.BooleanField()