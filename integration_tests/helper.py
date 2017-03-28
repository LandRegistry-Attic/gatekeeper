from functools import wraps
from gatekeeper.app import app
from flask.ext.script import Manager


def with_client(test):
    @wraps(test)
    def _wrapped_test(self):
        with self.app.test_client() as client:
            test(self, client)
    return _wrapped_test


def set_up_app(self):
    manager = Manager(app)
    self.app = manager.app
    self.manager = manager
    self.app.config['TESTING'] = True
