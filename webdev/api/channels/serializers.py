from rest_framework import serializers

from channels_app.models import Channel, Tag, Message


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Tag
        fields = ['name']


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    created_at = serializers.DateTimeField(read_only=True, format='%d %h %H:%M')

    class Meta:
        model = Message
        exclude = ['id', 'channel']


class ChannelSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    tags = TagSerializer(many=True)
    online = serializers.SerializerMethodField()
    date = serializers.DateTimeField(read_only=True, format='%d %h %Y')

    class Meta:
        model = Channel
        fields = ['name', 'description', 'author', 'date', 'tags', 'online']

    def get_online(self, obj: Channel) -> int:
        return obj.current_users.count()

    def create(self, validated_data) -> Channel:
        validated_data['author'] = self.context['request'].user
        tags_data = validated_data.pop('tags')
        channel = Channel.objects.create(**validated_data)
        for tag_data in tags_data:
            try:
                tag = Tag.objects.get(name=tag_data['name'])
            except Tag.DoesNotExist:
                return channel.delete()
            channel.tags.add(tag)
        return channel


class ChannelRetrieveSerializer(ChannelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        model = Channel
        fields = ['name', 'description', 'author', 'date', 'tags', 'online', 'messages']


class ChannelUpdateSerializer(ChannelSerializer):

    class Meta:
        model = Channel
        fields = ['name', 'description', 'tags']

    def update(self, instance, validated_data) -> Channel:
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        return instance
