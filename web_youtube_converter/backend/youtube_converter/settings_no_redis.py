from .settings import *

# Override Celery settings to use synchronous execution (for testing without Redis)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable Celery broker
CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None

print("Running in NO-REDIS mode - tasks will run synchronously")