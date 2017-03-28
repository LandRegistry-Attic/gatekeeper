import os
# RULES OF CONFIG:
# 1. No region specific code. Regions are defined by setting the OS environment variables appropriately to build up the
# desired behaviour.
# 2. No use of defaults when getting OS environment variables. They must all be set to the required values prior to the
# app starting.
# 3. This is the only file in the app where os.getenv should be used.

# For logging
FLASK_LOG_LEVEL = os.getenv('FLASK_LOG_LEVEL')
# For health route
COMMIT = os.getenv('COMMIT')

DEED_API_URL = os.getenv('DEED_API_URL')

LOGCONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s level=[%(levelname)s] traceid=[%(trace_id)s] ' +
                      'message=[%(message)s] exception=[%(exc_info)s]'
        },
        'audit': {
            'format': '%(asctime)s level=[AUDIT] traceid=[%(trace_id)s] message=[%(message)s]]'
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
