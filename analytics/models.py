from django.db import models


from django.db import models

class ToiletStatus(models.Model):
    toilet_id = models.IntegerField(primary_key=True)
    is_occupied = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Toilet {self.toilet_id}"