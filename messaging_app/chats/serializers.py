from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields =[
             'user_id',
             'username',
             'first_name',
             'last_name',
             'email',
             'phone_number',
             'role',
             'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)

    class Meta:
        model  =Message
        fields =[
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'sent_at'
        ]   
        read_only_fields = ['message_id', 'sent_at']

def validate_sender_id(self, value):
    if not User.objects.filter(user_id=value).exists():
        raise serializers.ValidationError("Sender does not exist.")
    return value

class ConversationListSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'message_count',
            'last_message',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

        
           