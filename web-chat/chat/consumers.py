import json
import random
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from message.models import Message

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.user = self.scope["user"]
        print(self.channel_layer)

        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    
    def receive(self, text_data):
       
        text_data_json = json.loads(text_data)
        message =  text_data_json['message'] + ' [ ' + str(datetime.now().strftime("%Y-%m-%d %H:%M")) +' ]'

        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.user.username
            }
        )
        Message.objects.create(body=message,sender=self.user)

    
    def chat_message(self, event):
        message = event['message']
        username = event['username']
        print(username)

    
        
        
        self.send(text_data=json.dumps({
            'message': message,
            'username' : username,
        }))