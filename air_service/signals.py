import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from air_service.models import Airplane


@receiver(pre_delete, sender=Airplane)
def delete_avatar(sender, instance, **kwargs):
    image = instance.image
    if image and hasattr(image, "path"):
        if os.path.isfile(image.path):
            os.remove(image.path)
