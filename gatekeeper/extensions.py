from flask_logconfig import LogConfig
import logging
from flask import g, ctx

# Create empty extension objects here
logger = LogConfig()


def register_extensions(app):
    """Adds any previously created extension objects into the app, and does any further setup they need."""
    # Logging
    logger.init_app(app)
    # Along with the default flask logger (app.logger) define a new one specifically for audit. To use this logger
    # just add app.audit_logger.info("an audit point").
    app.audit_logger = logging.getLogger("audit")

    # All done!
    app.logger.info("Extensions registered")


class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """Provide some extra variables to be placed into the log message."""

        # If we have an app context (because we're servicing an http request) then get the trace id we have
        # set in g (see app.py)
        if ctx.has_app_context():
            log_record.trace_id = g.trace_id
        else:
            log_record.trace_id = 'N/A'
        return True
