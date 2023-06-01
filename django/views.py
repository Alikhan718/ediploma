from django.http import JsonResponse
from django.views import View
from .models import Diploma
from .utils import generate_diploma

class DiplomaGeneratorView(View):
    def post(self, request):
        data = request.POST
        diploma = generate_diploma(data)
        diploma.save()
        return JsonResponse({'status': 'success', 'diploma_id': diploma.id})
