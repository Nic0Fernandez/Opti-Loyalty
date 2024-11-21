from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from histo.get_histo import get_histo

# Create your views here.


db_path = settings.DATABASES['default']['NAME']

@login_required
def histo(request):
    context = {
        'orders': get_histo(db_path,request.user.id),
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'histo/histo.html', context)