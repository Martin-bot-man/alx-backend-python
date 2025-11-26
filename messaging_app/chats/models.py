from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles basic user information and excludes sensitive fields.
    """
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at',
            'password',
        ]
        read_only_fields = ['user_id', 'created_at']
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        """
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        Update user and handle password changes.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for User model.
    Used for nested representations to avoid excessive data.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email', 'full_name']
        read_only_fields = ['user_id']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Includes nested sender information.
    """
    sender = UserBasicSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True
    )
    message_preview = serializers.CharField(source='get_message_preview', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'message_preview',
            'sent_at',
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """
        Ensure message body is not empty or just whitespace.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating messages.
    Simplified version without nested sender details.
    """
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    Includes nested participants and messages.
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='participants'
    )
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    conversation_title = serializers.CharField(source='get_conversation_title', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'message_count',
            'last_message',
            'conversation_title',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """
        Return the total number of messages in the conversation.
        """
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """
        Return the most recent message in the conversation.
        """
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def create(self, validated_data):
        """
        Create a conversation and add participants.
        """
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing conversations.
    Does not include all messages, only summary information.
    """
    participants = UserBasicSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_preview = serializers.CharField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'message_count',
            'last_message',
            'last_message_preview',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_message_count(self, obj):
        """
        Return the total number of messages in the conversation.
        """
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """
        Return a simplified version of the last message.
        """
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_id': str(last_message.message_id),
                'sender': last_message.sender.username,
                'message_body': last_message.message_body[:50] + '...' if len(last_message.message_body) > 50 else last_message.message_body,
                'sent_at': last_message.sent_at
            }
        return None