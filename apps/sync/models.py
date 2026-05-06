import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Department(models.Model):
    """
    Département / filière venant de l'ERP simulé.
    Exemple : Génie Logiciel, Réseaux, IA, etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sync_departments"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicSemester(models.Model):
    """
    Semestre académique venant de l'ERP simulé.
    Exemple : Semestre 1 - 2025/2026.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sync_academic_semesters"
        ordering = ["-start_date"]

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError("La date de début doit être inférieure à la date de fin.")

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class TeacherSync(models.Model):
    """
    Enseignant synchronisé depuis l'ERP simulé.
    Ces données représentent la source officielle côté école.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university_id = models.CharField(max_length=80, unique=True)
    matricule = models.CharField(max_length=80, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="teachers",
    )

    grade = models.CharField(max_length=100, blank=True, null=True)
    specialty = models.CharField(max_length=150, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sync_teachers"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["university_id"]),
            models.Index(fields=["matricule"]),
            models.Index(fields=["email"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} - {self.matricule}"


class StudentSync(models.Model):
    """
    Étudiant synchronisé depuis l'ERP simulé.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university_id = models.CharField(max_length=80, unique=True)
    student_code = models.CharField(max_length=80, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True, null=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students",
    )

    level = models.CharField(max_length=50)
    cohort = models.CharField(max_length=80)

    is_active = models.BooleanField(default=True)
    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sync_students"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["university_id"]),
            models.Index(fields=["student_code"]),
            models.Index(fields=["email"]),
            models.Index(fields=["level", "cohort"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} - {self.student_code}"


class CourseSync(models.Model):
    """
    Cours / module venant de l'ERP simulé.
    Un cours est affecté à un enseignant pour un semestre.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    university_id = models.CharField(max_length=80, unique=True)

    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True, null=True)

    teacher = models.ForeignKey(
        TeacherSync,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    semester = models.ForeignKey(
        AcademicSemester,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    level = models.CharField(max_length=50)
    cohort = models.CharField(max_length=80)
    credit = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    synced_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sync_courses"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["university_id"]),
            models.Index(fields=["code"]),
            models.Index(fields=["teacher"]),
            models.Index(fields=["semester"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class StudentCourseEnrollment(models.Model):
    """
    Inscription d'un étudiant à un cours.
    C'est ce modèle qui permettra de savoir si un étudiant peut évaluer un enseignant.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    student = models.ForeignKey(
        StudentSync,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    course = models.ForeignKey(
        CourseSync,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    semester = models.ForeignKey(
        AcademicSemester,
        on_delete=models.PROTECT,
        related_name="enrollments",
    )

    is_active = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sync_student_course_enrollments"
        unique_together = ("student", "course", "semester")
        ordering = ["-enrolled_at"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course"]),
            models.Index(fields=["semester"]),
        ]

    def clean(self):
        if self.course and self.semester and self.course.semester_id != self.semester_id:
            raise ValidationError("Le semestre de l'inscription doit correspondre au semestre du cours.")

    def __str__(self):
        return f"{self.student.full_name} → {self.course.code}"


class SyncLog(models.Model):
    """
    Journal des synchronisations ERP simulées.
    Même si on simule l'ERP, ce log donne une trace professionnelle des imports.
    """

    class SyncType(models.TextChoices):
        FULL = "FULL", "Synchronisation complète"
        PARTIAL = "PARTIAL", "Synchronisation partielle"
        MANUAL = "MANUAL", "Import manuel"

    class SyncStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "Succès"
        FAILED = "FAILED", "Échec"
        RUNNING = "RUNNING", "En cours"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sync_type = models.CharField(max_length=20, choices=SyncType.choices, default=SyncType.MANUAL)
    status = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.SUCCESS)

    teachers_count = models.PositiveIntegerField(default=0)
    students_count = models.PositiveIntegerField(default=0)
    courses_count = models.PositiveIntegerField(default=0)
    enrollments_count = models.PositiveIntegerField(default=0)

    message = models.TextField(blank=True, null=True)
    errors = models.JSONField(blank=True, null=True)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "sync_logs"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.sync_type} - {self.status} - {self.started_at}"