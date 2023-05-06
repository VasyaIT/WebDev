from .models import Channel
from webdev.celery import app


@app.task
def delete_messages():
    for channel in Channel.objects.all():
        mess = channel.messages
        if mess.count() > 10:
            messages = mess.order_by('-id')[:10]
            channel.messages.exclude(id__in=[message.id for message in messages]).delete()
