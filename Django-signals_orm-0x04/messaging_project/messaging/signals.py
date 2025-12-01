from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """Create a notification when a new message is sent."""
    if created:
        notification_content = f'New message from {instance.sender.username}':
        if len(instance.content)> 50:
            notification_content +="..."

        Notification.objects.create(
            user = instance.receiver,
            message =instance,
            notification_type ='message',
            content = notification_content,
            timestamp = instance.timestamp
        )    
