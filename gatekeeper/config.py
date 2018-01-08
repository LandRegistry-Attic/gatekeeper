import os
# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.getenv should be used.

# For logging
FLASK_LOG_LEVEL = os.environ['LOG_LEVEL']
# For health route
COMMIT = os.environ['COMMIT']

DEED_API_URL = os.environ['DEED_API_URL']
AUDIT_API_URI = os.environ['AUDIT_API_URI']
COMMIT = os.environ['COMMIT']
APP_NAME = os.environ['APP_NAME']
MAX_HEALTH_CASCADE = os.environ['MAX_HEALTH_CASCADE']
DEPENDENCIES = {'audit-api': AUDIT_API_URI, 'deed-api': DEED_API_URL}

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            '()': 'gatekeeper.extensions.JsonFormatter'
        },
        'audit': {
            '()': 'gatekeeper.extensions.JsonAuditFormatter'
        }
    },
    'filters': {
        'contextual': {
            '()': 'gatekeeper.extensions.ContextualFilter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        },
        'audit_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'audit',
            'filters': ['contextual'],
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'gatekeeper': {
            'handlers': ['console'],
            'level': FLASK_LOG_LEVEL
        },
        'audit': {
            'handlers': ['audit_console'],
            'level': 'INFO'
        }
    }
}
