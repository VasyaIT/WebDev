from loguru import logger

from django.conf import settings

logger.add((settings.BASE_DIR / 'logs/main.log'),
           format='{time:D MMMM - YYYY > HH:mm:ss} | {file} | {level} | {message}',
           rotation='10 MB', compression='zip', serialize=False)
