from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Max, Prefetch
from django.shortcuts import get_object_or_404

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer,
    UserBasicSerializer,
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)
from .permissions import IsConversationParticipant, IsMessageOwner


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User operations.
    Provides CRUD operations for users with search and filtering.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Optimize queries by selecting only necessary fields."""
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active users (non-admin filter example)."""
        queryset = self.get_queryset().filter(role__in=['user', 'moderator'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation operations.
    Provides endpoints to manage conversations with proper permissions.
    """
    permission_classes = [IsAuthenticated, IsConversationParticipant]
    lookup_field = 'conversation_id'
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Return conversations where current user is a participant."""
        user = self.request.user
        return Conversation.objects.filter(
            participants=user
        ).prefetch_related(
            'participants',
            Prefetch(
                'messages',
                queryset=Message.objects.select_related('sender').order_by('-sent_at')[:10]
            )
        ).annotate(
            last_message_time=Max('messages__sent_at')
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation with participants."""
        participant_ids = request.data.get('participant_ids', [])
        
        # Ensure current user is included
        if request.user.user_id not in participant_ids:
            participant_ids.append(str(request.user.user_id))
        
        # Validate minimum participants
        if len(participant_ids) < 2:
            return Response(
                {'detail': 'A conversation must have at least 2 participants.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all users exist
        users = User.objects.filter(user_id__in=participant_ids)
        if users.count() != len(participant_ids):
            return Response(
                {'detail': 'One or more participants do not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create conversation and add participants
        conversation = Conversation.objects.create()
        conversation.participants.set(users)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific conversation with permission check."""
        conversation = self.get_object()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """Add a new participant to a conversation."""
        conversation = self.get_object()
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, user_id=user_id)
        
        if conversation.participants.filter(user_id=user_id).exists():
            return Response(
                {'detail': 'User is already a participant.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.participants.add(user)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """Remove a participant from a conversation."""
        conversation = self.get_object()
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'detail': 'user_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent removing the last participant
        if conversation.participants.count() <= 2:
            return Response(
                {'detail': 'Conversation must have at least 2 participants.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, user_id=user_id)
        conversation.participants.remove(user)
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get conversations ordered by most recent message."""
        conversations = self.get_queryset().order_by('-last_message_time')
        page = self.paginate_queryset(conversations)
        if page is not None:
            serializer = ConversationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message operations.
    Provides endpoints to manage messages with proper access control.
    """
    permission_classes = [IsAuthenticated, IsMessageOwner]
    lookup_field = 'message_id'
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        user = self.request.user
        queryset = Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation')
        
        # Filter by conversation if provided
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for create and read operations."""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """Send a new message to a conversation."""
        conversation_id = request.data.get('conversation')
        
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        # Verify user is a participant
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'detail': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data.copy()
        data['sender'] = request.user.user_id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        output_serializer = MessageSerializer(message)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific message with permission check."""
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update a message (only sender can update)."""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'detail': 'You can only update your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a message (only sender can delete)."""
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'detail': 'You can only delete your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def conversation_messages(self, request):
        """Get all messages for a specific conversation."""
        conversation_id = request.query_params.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'detail': 'conversation_id parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        # Check participation
        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response(
                {'detail': 'You are not a participant in this conversation.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = self.get_queryset().filter(conversation=conversation)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search messages by content."""
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'detail': 'Search query (q) parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(message_body__icontains=query)
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)