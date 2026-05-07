from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.authentication.permissions import IsAdminOrDirector
from .models import EvaluationCampaign
from .serializers import EvaluationCampaignSerializer
from .services import CampaignService


class EvaluationCampaignViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCampaign.objects.select_related(
        "semester",
        "created_by",
    ).all()
    serializer_class = EvaluationCampaignSerializer
    permission_classes = [IsAdminOrDirector]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "title",
        "description",
        "semester__name",
        "status",
    ]
    ordering_fields = [
        "title",
        "status",
        "start_date",
        "end_date",
        "created_at",
    ]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        campaign = self.get_object()

        try:
            campaign = CampaignService.activate_campaign(campaign)
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            EvaluationCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        campaign = self.get_object()

        try:
            campaign = CampaignService.close_campaign(campaign)
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            EvaluationCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        campaign = self.get_object()

        try:
            campaign = CampaignService.cancel_campaign(campaign)
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            EvaluationCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )