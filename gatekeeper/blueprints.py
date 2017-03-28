# Import every blueprint file
from gatekeeper.views import general, deed_gatekeeper
from gatekeeper import exceptions


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(deed_gatekeeper.deed_gatekeeper, url_prefix='/deed')
    app.register_blueprint(exceptions.exceptions)

    # All done!
    app.logger.info("Blueprints registered")
