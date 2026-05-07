from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import EvaluationCampaign


class CampaignService:
    """
    Service métier pour gérer le cycle de vie des campagnes.
    """

    @staticmethod
    @transaction.atomic
    def activate_campaign(campaign: EvaluationCampaign) -> EvaluationCampaign:
        if campaign.status != EvaluationCampaign.Status.DRAFT:
            raise ValidationError("Seule une campagne en brouillon peut être activée.")

        now = timezone.now()

        if campaign.end_date <= now:
            raise ValidationError("Impossible d'activer une campagne déjà expirée.")

        campaign.status = EvaluationCampaign.Status.ACTIVE
        campaign.save(update_fields=["status", "updated_at"])
        return campaign

    @staticmethod
    @transaction.atomic
    def close_campaign(campaign: EvaluationCampaign) -> EvaluationCampaign:
        if campaign.status not in [
            EvaluationCampaign.Status.ACTIVE,
            EvaluationCampaign.Status.DRAFT,
        ]:
            raise ValidationError("Cette campagne ne peut pas être clôturée.")

        campaign.status = EvaluationCampaign.Status.CLOSED
        campaign.save(update_fields=["status", "updated_at"])
        return campaign

    @staticmethod
    @transaction.atomic
    def cancel_campaign(campaign: EvaluationCampaign) -> EvaluationCampaign:
        if campaign.status == EvaluationCampaign.Status.CLOSED:
            raise ValidationError("Une campagne déjà clôturée ne peut pas être annulée.")

        campaign.status = EvaluationCampaign.Status.CANCELLED
        campaign.save(update_fields=["status", "updated_at"])
        return campaign