from django.db import models

class Diploma(models.Model):
    name = models.CharField(max_length=255)
    degree_en = models.CharField(max_length=255)
    degree_ru = models.CharField(max_length=255)
    degree_kz = models.CharField(max_length=255)
    study_time_ru = models.CharField(max_length=255)
    study_time_en = models.CharField(max_length=255)
    study_time_kz = models.CharField(max_length=255)
    diploma_image = models.ImageField(upload_to='diplomas/')
    json_data = models.JSONField()