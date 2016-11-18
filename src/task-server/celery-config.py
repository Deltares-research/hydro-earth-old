CELERY_RESULT_BACKEND = 'mongodb://localhost:81/'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'database': 'meteor',
    'taskmeta_collection': 'celery-results',
}

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']

