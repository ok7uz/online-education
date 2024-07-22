from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from config.utils import TimestampField
from .models import Chat, Message
from ..accounts.models import User
from ..accounts.serializers import UserListSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(read_only=True, source='sender.username')
    created_at = TimestampField(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender_username', 'content', 'media', 'media_type', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserListSerializer(many=True, read_only=True)
    created_at = TimestampField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'is_group', 'created_at', 'messages']


class ChatListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, help_text='Username of the participant')
    participants = UserListSerializer(many=True, read_only=True)
    created_at = TimestampField(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'is_group', 'username', 'participants', 'created_at']

    def create(self, validated_data):
        username = validated_data.pop('username')
        participant_user = get_object_or_404(User, username=username)
        chat = Chat.objects.create(name='testing')
        chat.participants.add(participant_user, self.context['request'].user)
        return chat
