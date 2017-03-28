# This file is the entry point.
# First we import the app object, which will get initialised as we do it. Then import methods we're about to use.
from gatekeeper.app import app
from gatekeeper.extensions import register_extensions
from gatekeeper.blueprints import register_blueprints

# Now we register any extensions we use into the app
register_extensions(app)
# Finally we register our blueprints to get our routes up and running.
register_blueprints(app)
