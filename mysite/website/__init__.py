from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from website.config import Config
from flask_mail import Mail


# Initialise the database
db = SQLAlchemy()

# Hashing class
bcrypt = Bcrypt()

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

# Email
mail = Mail()


#
def create_app(config=Config):
    # Initialise the app
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from website.users.routes import users
    from website.admin.routes import admin
    from website.supplier.routes import supplier
    from website.others.routes import others
    from website.main.routes import main
    from website.actions.routes import action
    from website.errors.routes import errors

    app.register_blueprint(users)
    app.register_blueprint(admin)
    app.register_blueprint(supplier)
    app.register_blueprint(others)
    app.register_blueprint(main)
    app.register_blueprint(action)
    app.register_blueprint(errors)

    return app

