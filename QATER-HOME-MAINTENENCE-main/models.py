from itsdangerous import URLSafeTimedSerializer as Serializer
from . import db
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from datetime import datetime , timedelta
import random




class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    ar_title = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String, nullable=False, unique=True)
    img_url = db.Column(db.String, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    steps = db.relationship('Step', back_populates='service', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', back_populates='service', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Service {self.title}>'



class Step(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False, unique=False)

    
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=True)

    service = db.relationship('Service', back_populates='steps', lazy=True)

    def __repr__(self):
        return f'Booking for {self.service.title}: {self.name}, {self.ph_number}'
    



class Role(enum.Enum):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False) 
    password_hash = db.Column(db.String(256), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)  
    verification_expiry = db.Column(db.DateTime, nullable=True)
    reset_code = db.Column(db.String(6), nullable=True) 
    reset_expiry = db.Column(db.DateTime, nullable=True)
    
    role = db.Column(db.Enum(Role, native_enum=False), nullable=False, default=Role.ADMIN)

    def generate_verification_code(self):
        code = ''.join(random.choices('0123456789', k=6))  
        self.verification_code = code
        self.verification_expiry = datetime.utcnow() + timedelta(minutes=30)  
        return code
    
    def generate_reset_code(self):
        code = ''.join(random.choices('0123456789', k=6))
        self.reset_code = code
        self.reset_expiry = datetime.utcnow() + timedelta(minutes=30)
        return code

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_super_admin(self):
        return self.role == Role.SUPER_ADMIN
    
    def is_admin(self):
        return self.role in [Role.ADMIN, Role.SUPER_ADMIN]
    
    # Flask-Login required methods
    def is_active(self):
        return True 

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True  

    def is_anonymous(self):
        return False
    
    def __repr__(self):  # Added: For easier debugging (e.g., print(user))
        return f'<User {self.username}>'
    






class BookingStatus(enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'


class Booking(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    ph_number = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    status = db.Column(
        db.Enum(BookingStatus, native_enum=False), 
        nullable=False, 
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value
    )

    handled_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    handler = db.relationship('User', backref='handled_bookings')
    


    handled_by_username = db.Column(db.String(150), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    service = db.relationship('Service', back_populates='bookings', lazy=True)

    def __repr__(self):
        return f'{self.message}'