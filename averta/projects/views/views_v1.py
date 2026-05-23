from django.http import HttpResponse


def homepage(request):
    return HttpResponse('<h1>Averta</h1><p>Homepage</p>')
