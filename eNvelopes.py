import os
from application import create_app, db
from application.models import User, Role, Transaction, Category, Payee
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default') # uses configuration from env if set, else default used
migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Transaction=Transaction, Category=Category, Payee=Payee)

@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
