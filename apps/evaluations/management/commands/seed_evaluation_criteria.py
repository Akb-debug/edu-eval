from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.evaluations.models import EvaluationCriteria


class Command(BaseCommand):
    help = "Crée les critères d'évaluation par défaut."

    DEFAULT_CRITERIA = [
        {
            "name": "Clarté des explications",
            "description": "Capacité de l’enseignant à expliquer clairement les notions du cours.",
            "category": EvaluationCriteria.Category.PEDAGOGY,
            "weight": Decimal("20.00"),
        },
        {
            "name": "Maîtrise du contenu",
            "description": "Niveau de maîtrise du cours et exactitude des explications données.",
            "category": EvaluationCriteria.Category.CONTENT,
            "weight": Decimal("20.00"),
        },
        {
            "name": "Organisation du cours",
            "description": "Respect du programme, structuration du cours et progression pédagogique.",
            "category": EvaluationCriteria.Category.ORGANIZATION,
            "weight": Decimal("15.00"),
        },
        {
            "name": "Interaction avec les étudiants",
            "description": "Capacité à encourager les questions, échanges et participation.",
            "category": EvaluationCriteria.Category.PEDAGOGY,
            "weight": Decimal("15.00"),
        },
        {
            "name": "Disponibilité",
            "description": "Disponibilité de l’enseignant pour accompagner les étudiants hors cours.",
            "category": EvaluationCriteria.Category.AVAILABILITY,
            "weight": Decimal("15.00"),
        },
        {
            "name": "Ponctualité et respect des horaires",
            "description": "Respect des horaires de début et de fin des séances.",
            "category": EvaluationCriteria.Category.BEHAVIOR,
            "weight": Decimal("15.00"),
        },
    ]

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in self.DEFAULT_CRITERIA:
            criteria, created = EvaluationCriteria.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "category": item["category"],
                    "weight": item["weight"],
                    "is_active": True,
                    "version": 1,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Critères créés : {created_count} | Critères mis à jour : {updated_count}"
            )
        )