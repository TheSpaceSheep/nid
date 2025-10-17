from django.db import models


class User(models.Model):
    NAMES = [
        ("noe", "Noé"),
        ("baz", "Baz"),
        ("philo", "Philo"),
        ("maya", "Maya"),
        ("jules", "Jules"),
        ("clotilde", "Clotilde"),
        ("pierre", "Pierre"),
        ("lorene", "Lorene"),
    ]

    name = models.CharField(max_length=20, choices=NAMES, unique=True)

    def __str__(self):
        return self.get_name_display()

    class Meta:
        ordering = ["name"]
