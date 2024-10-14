To create a full project using WebSocket with Django, you typically use Django Channels, which extends Django to handle WebSockets, allowing you to work with asynchronous communication. Below is a step-by-step guide to building a basic WebSocket-based project in Django.

Prerequisites
Before starting, ensure you have Python and Django installed on your system.

bash

pip install django
Additionally, install Django Channels and ASGI:

bash

pip install channels
Step 1: Create a Django Project
Start by creating a new Django project:

bash

django-admin startproject websocket_project
cd websocket_project
Step 2: Create a Django App
Create a new Django app that will handle WebSocket communication.

bash

python manage.py startapp chat
Step 3: Configure Django Channels
In the settings.py file of your project, modify it to add channels and configure the ASGI application.

python

# websocket_project/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # Add channels here
    'chat',  # Add your app here
]

# ASGI application
ASGI_APPLICATION = 'websocket_project.asgi.application'

# Channels Layer (in-memory for now)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

Next, create the asgi.py file if it's not already present:

python

# websocket_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
Step 4: Create WebSocket Consumer
Create a consumer to handle WebSocket connections. Consumers are similar to Django views but handle WebSocket connections.

In chat/consumers.py:

python

# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join room group
        await self.channel_layer.group_add(
            'chat_room',  # Static room name for now
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            'chat_room',
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            'chat_room',
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
Step 5: Define Routing
In chat/routing.py, define the WebSocket routing for the ChatConsumer.

python

# chat/routing.py

from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', ChatConsumer.as_asgi()),  # WebSocket route
]
Step 6: Create a Simple Template to Test WebSocket
Create an HTML file that will connect to the WebSocket. In chat/templates/chat/room.html:

html

<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat</title>
</head>
<body>
    <h1>WebSocket Chat Room</h1>
    <textarea id="chat-log" cols="100" rows="20" readonly></textarea><br>
    <input id="chat-message-input" type="text" size="100"><br>
    <button id="send-button">Send</button>

    <script>
        const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/');

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            document.querySelector('#chat-log').value += (data.message + '\n');
        };

        document.querySelector('#send-button').onclick = function() {
            const messageInput = document.querySelector('#chat-message-input');
            const message = messageInput.value;
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInput.value = '';
        };
    </script>
</body>
</html>
Step 7: Create Views and URL Patterns
In chat/views.py, create a simple view to render the chat page:

python

# chat/views.py

from django.shortcuts import render

def room(request):
    return render(request, 'chat/room.html')
Add the URL route in chat/urls.py:

python

# chat/urls.py

from django.urls import path
from .views import room

urlpatterns = [
    path('chat/', room, name='room'),
]
In the project’s urls.py, include the chat URLs:

python

# websocket_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
]
Step 8: Run the Project
Apply migrations and run the server:

bash

python manage.py migrate
python manage.py runserver
Open your browser and go to http://localhost:8000/chat/. You should see the WebSocket chat interface. You can now send and receive messages using WebSockets.

Step 9: Test WebSocket
You can test this WebSocket chat by opening the page in multiple browser tabs and sending messages. Each tab will receive the messages in real time.

Step 10: Deploy with Daphne
For production, Django Channels uses Daphne to run the ASGI application. Install Daphne:

bash

pip install daphne
Then, run Daphne:

bash

daphne -b 0.0.0.0 -p 8000 websocket_project.asgi:application
