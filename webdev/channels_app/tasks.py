from .models import Channel
from webdev.celery import app

from webdev.logger_config import logger


@app.task
def delete_messages():
    for channel in Channel.objects.all():
        mess = channel.messages
        if len(mess) > 10:
            messages = mess.order_by('-id')[:10]
            channel.messages.exclude(id__in=[message.id for message in messages]).delete()
            logger.success('Task delete message complete')
