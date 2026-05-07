from django.contrib import admin

from .models import EvaluationCampaign


@admin.register(EvaluationCampaign)
class EvaluationCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "semester",
        "status",
        "start_date",
        "end_date",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "semester")
    search_fields = ("title", "description", "semester__name", "created_by__email")
    readonly_fields = ("created_at", "updated_at")