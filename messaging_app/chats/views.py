from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserBasicSerializer,
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations.
    Provides CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    
    def get_queryset(self):
        """
        Optionally filter users by role or search term.
        """
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        search = self.request.query_params.get('search', None)
        
        if role:
            queryset = queryset.filter(role=role)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current authenticated user's profile.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation operations.
    Provides endpoints to list, create, retrieve, update, and delete conversations.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'conversation_id'
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant.
        """
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related(
            'participants',
            'messages',
            'messages__sender'
        ).distinct()
    
    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        Automatically adds the creator as a participant.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get participant IDs from request
        participant_ids = request.data.get('participant_ids', [])
        
        # Ensure current user is included in participants
        if request.user.user_id not in participant_ids:
            participant_ids.append(request.user.user_id)
        
        # Validate minimum participants
        if len(participant_ids) < 2:
            return Response(
                {'error': 'A conversation must have at least 2 participants.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create conversation
        conversation = Conversation.objects.create()
        conversation.participants.set(participant_ids)
        
        # Return serialized conversation
        output_serializer = ConversationSerializer(conversation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific conversation with all messages.
        """
        conversation = self.get_object()
        
        # Check if user is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """
        Add a new participant to an existing conversation.
        """
        conversation = self.get_object()
        
        # Check if requester is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """
        Remove a participant from a conversation.
        """
        conversation = self.get_object()
        
        # Check if requester is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            
            # Prevent removing the last participant
            if conversation.participants.count() <= 2:
                return Response(
                    {'error': 'Cannot remove participant. Conversation must have at least 2 participants.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conversation.participants.remove(user)
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get conversations ordered by most recent message.
        """
        conversations = self.get_queryset().annotate(
            last_message_time=Max('messages__sent_at')
        ).order_by('-last_message_time')
        
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations.
    Provides endpoints to list, create, retrieve, update, and delete messages.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'message_id'
    
    def get_queryset(self):
        """
        Return messages from conversations where the user is a participant.
        Optionally filter by conversation_id.
        """
        user = self.request.user
        queryset = Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation')
        
        # Filter by conversation if provided
        conversation_id = self.request.query_params.get('conversation_id', None)
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset.order_by('sent_at')
    
    def get_serializer_class(self):
        """
        Use different serializers for create and read operations.
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        """
        # Set the sender to the current user
        data = request.data.copy()
        data['sender'] = request.user.user_id
        
        serializer = MessageCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = data.get('conversation')
        
        # Verify conversation exists
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Save the message
        message = serializer.save()
        
        # Return with full message serialization
        output_serializer = MessageSerializer(message)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific message.
        """
        message = self.get_object()
        
        # Check if user is a participant in the conversation
        if request.user not in message.conversation.participants.all():
            return Response(
                {'error': 'You do not have access to this message.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update a message (only by the sender).
        """
        message = self.get_object()
        
        # Only the sender can update the message
        if message.sender != request.user:
            return Response(
                {'error': 'You can only update your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a message (only by the sender).
        """
        message = self.get_object()
        
        # Only the sender can delete the message
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def conversation_messages(self, request):
        """
        Get all messages for a specific conversation.
        """
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user is a participant
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = self.get_queryset().filter(conversation=conversation)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search messages by content.
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Search query (q) parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            message_body__icontains=query
        )
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)