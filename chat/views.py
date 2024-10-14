from django.shortcuts import render

# Create your views here.
# chat/views.py


def room(request):
    return render(request, 'chat/room.html')
