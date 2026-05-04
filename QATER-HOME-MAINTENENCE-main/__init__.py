from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from flask_migrate import Migrate
import os
import cloudinary
from flask_sitemap import Sitemap 
from flask_limiter.util import get_remote_address
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
ext = Sitemap()
mail = Mail()




login_manager.login_view = 'admin.authenticate'

@login_manager.user_loader
def load_user(user_id):
    from .models import User 
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')  

  
    
    # Sitemap config
    app.config['SITEMAP_URL_SCHEME'] = 'https'
    app.config['SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS'] = False  
    app.config['SERVER_NAME'] = os.environ.get('BASE_URL').split('://')[1] if os.environ.get('BASE_URL') else None  
    app.config['SITEMAP_IGNORE_ENDPOINTS'] = [
        'admin.user_management',
        'admin.add_user',
        'admin.profile',
        'admin.authenticate',
        'admin.dashboard',
        'admin.logout',
        'admin.services',
        'admin.create_service'
    ]
    ext.init_app(app)


    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    

    # Register blueprints
    from app.main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Sitemap route
    @app.route('/sitemap.xml')
    def sitemap():
        return ext.generate()

    @app.context_processor
    def inject_roles():
        from .models import Role, BookingStatus
        return dict(Role=Role, BookingStatus=BookingStatus)

    return app