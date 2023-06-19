from django.urls import path
from .views import DiplomaGeneratorView

urlpatterns = [
    path('generate/', DiplomaGeneratorView.as_view(), name='generate_diploma'),
]