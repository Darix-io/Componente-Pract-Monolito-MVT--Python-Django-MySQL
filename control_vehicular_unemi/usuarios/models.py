from django.db import models
from django.contrib.auth.models import AbstractUser

class RolEnum(models.TextChoices):
    ADMINISTRADOR = 'Administrador', 'Administrador'
    PERSONAL_SEGURIDAD = 'Personal_seguridad', 'Personal_seguridad'

class Usuario(AbstractUser):
    cedula = models.CharField(max_length=20, unique=True)
    id_rol = models.CharField(
        max_length=50,
        choices=RolEnum.choices,
        default=RolEnum.PERSONAL_SEGURIDAD
    )

    # Corregimos los campos que causaban el conflicto de nombres
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions_set',
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.cedula}"