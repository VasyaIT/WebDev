from loguru import logger

logger.add('logs/main.log', format='{time:D MMMM - YYYY > HH:mm:ss} | {file} | {level} | {message}',
           rotation='10 MB', compression='zip', serialize=False)
