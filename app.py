from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dreamhome.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(10), unique=True, nullable=False)  # DH000001 format
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    properties = db.relationship('Property', backref='owner', foreign_keys='Property.owner_id')
    listed_properties = db.relationship('Property', backref='agent', foreign_keys='Property.agent_id')
    saved_properties = db.relationship('SavedProperty', backref='user', lazy=True)
    inquiries = db.relationship('Inquiry', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    saved_searches = db.relationship('SavedSearch', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    property_type = db.Column(db.String(50), nullable=False)  # house, apartment, commercial, land
    transaction_type = db.Column(db.String(20), nullable=False)  # sale, rent
    price = db.Column(db.Float, nullable=False)
    area = db.Column(db.Float, nullable=False)  # in square feet/meters
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    location = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zipcode = db.Column(db.String(20), nullable=False)
    amenities = db.Column(db.Text)  # JSON string of amenities
    images = db.Column(db.Text)  # JSON string of image URLs
    status = db.Column(db.String(20), default='available')  # available, under contract, sold, rented
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    saved_by = db.relationship('SavedProperty', backref='property', lazy=True)
    inquiries = db.relationship('Inquiry', backref='property', lazy=True)
    appointments = db.relationship('Appointment', backref='property', lazy=True)
    purchase_requests = db.relationship('PropertyPurchase', backref='property', lazy=True)

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, responded, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavedProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    activity_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.Text)  # JSON string of search criteria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PropertyPurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes for User Authentication
@app.route('/register', methods=['GET', 'POST'])
@login_required  # Only logged-in admins can create new users
def register():
    if not current_user.is_admin:
        flash('Access denied. Only administrators can create new users.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')  # 'user', 'agent', or 'admin'
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            is_admin=(role == 'admin'),
            is_active=True
        )
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Generate unique ID for the user
        unique_id = f"DH{user.id:06d}"  # DH000001, DH000002, etc.
        user.user_id = unique_id
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account created successfully. User ID: {unique_id}', 'success')
        return redirect(url_for('manage_users'))
        
    return render_template('admin/create_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'agent':
            return redirect(url_for('agent_dashboard'))
        else:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter(
            (User.email == login_id) | (User.user_id == login_id)
        ).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Your account is inactive. Please contact the administrator.', 'danger')
                return redirect(url_for('login'))

            login_user(user, remember=remember)
            
            # Log the login activity
            activity = ActivityLog(
                user_id=user.id,
                activity_type='login',
                description=f'User logged in from IP: {request.remote_addr}',
                timestamp=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()

            # Redirect based on role
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'agent':
                return redirect(url_for('agent_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# User Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's saved searches
    saved_searches = SavedSearch.query.filter_by(user_id=current_user.id).all()
    
    # Get user's purchase requests
    purchase_requests = PropertyPurchase.query.filter_by(user_id=current_user.id).all()
    
    # Get featured properties
    featured_properties = Property.query.filter_by(featured=True).limit(3).all()
    
    # Get user's recent activities
    activities = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    # Get user's appointments
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('dashboard.html',
                         saved_searches=saved_searches,
                         purchase_requests=purchase_requests,
                         featured_properties=featured_properties,
                         activities=activities,
                         appointments=appointments)

@app.route('/agent/dashboard')
@login_required
def agent_dashboard():
    if current_user.role != 'agent':
        flash('Access denied. Agent privileges required.', 'danger')
        return redirect(url_for('dashboard'))
    
    properties = Property.query.filter_by(agent_id=current_user.id).all()
    inquiries = Inquiry.query.join(Property).filter(Property.agent_id == current_user.id).all()
    appointments = Appointment.query.join(Property).filter(Property.agent_id == current_user.id).all()

    return render_template('agent_dashboard.html',
                         properties=properties,
                         inquiries=inquiries,
                         appointments=appointments)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    properties = Property.query.all()
    users = User.query.all()
    inquiries = Inquiry.query.all()
    appointments = Appointment.query.all()
    
    return render_template('admin_dashboard.html',
                         properties=properties,
                         users=users,
                         inquiries=inquiries,
                         appointments=appointments)

# Routes for Properties
@app.route('/properties')
def properties():
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Build the query
    query = Property.query

    # Apply filters
    if location := request.args.get('location'):
        query = query.filter(Property.location.ilike(f'%{location}%'))
    
    if property_type := request.args.get('property_type'):
        query = query.filter(Property.property_type == property_type)
    
    if transaction_type := request.args.get('transaction_type'):
        query = query.filter(Property.transaction_type == transaction_type)
    
    if min_price := request.args.get('min_price'):
        query = query.filter(Property.price >= float(min_price))
    
    if max_price := request.args.get('max_price'):
        query = query.filter(Property.price <= float(max_price))
    
    if bedrooms := request.args.get('bedrooms'):
        query = query.filter(Property.bedrooms >= int(bedrooms))
    
    if bathrooms := request.args.get('bathrooms'):
        query = query.filter(Property.bathrooms >= float(bathrooms))
    
    if min_area := request.args.get('min_area'):
        query = query.filter(Property.area >= float(min_area))
    
    if max_area := request.args.get('max_area'):
        query = query.filter(Property.area <= float(max_area))

    # Apply sorting
    if sort := request.args.get('sort'):
        if sort == 'price_asc':
            query = query.order_by(Property.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Property.price.desc())
        elif sort == 'date_desc':
            query = query.order_by(Property.created_at.desc())
        elif sort == 'date_asc':
            query = query.order_by(Property.created_at.asc())
    else:
        # Default sorting: newest first
        query = query.order_by(Property.created_at.desc())

    # Paginate results
    properties = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('properties.html', properties=properties)

@app.route('/property/<int:property_id>')
def view_property(property_id):
    property = Property.query.get_or_404(property_id)
    similar_properties = Property.query.filter(
        Property.id != property_id,
        Property.property_type == property.property_type,
        Property.transaction_type == property.transaction_type,
        Property.price.between(property.price * 0.8, property.price * 1.2)
    ).limit(3).all()
    
    is_saved = False
    if current_user.is_authenticated:
        is_saved = SavedProperty.query.filter_by(
            user_id=current_user.id,
            property_id=property_id
        ).first() is not None
    
    return render_template('view_property.html', 
                         property=property, 
                         similar_properties=similar_properties,
                         is_saved=is_saved)

@app.route('/api/properties/<int:property_id>/toggle_saved', methods=['POST'])
@login_required
def toggle_saved_property(property_id):
    saved = SavedProperty.query.filter_by(
        user_id=current_user.id,
        property_id=property_id
    ).first()
    
    if saved:
        db.session.delete(saved)
        db.session.commit()
        return jsonify({'success': True, 'saved': False})
    else:
        saved = SavedProperty(user_id=current_user.id, property_id=property_id)
        db.session.add(saved)
        db.session.commit()
        return jsonify({'success': True, 'saved': True})

@app.route('/agents')
def agents():
    page = request.args.get('page', 1, type=int)
    agents = User.query.filter_by(is_agent=True).paginate(
        page=page, per_page=12, error_out=False
    )
    return render_template('agents.html', agents=agents)

@app.route('/agent/<int:agent_id>')
def agent_profile(agent_id):
    agent = User.query.get_or_404(agent_id)
    if not agent.is_agent:
        abort(404)
    
    properties = Property.query.filter_by(agent_id=agent_id).all()
    return render_template('agent_profile.html', agent=agent, properties=properties)

@app.route('/my_properties')
@login_required
def my_properties():
    user_properties = Property.query.filter_by(owner_id=current_user.id).all()
    return render_template('my_properties.html', properties=user_properties)

@app.route('/my_inquiries')
@login_required
def my_inquiries():
    user_inquiries = Inquiry.query.filter_by(user_id=current_user.id).all()
    return render_template('my_inquiries.html', inquiries=user_inquiries)

@app.route('/my_appointments')
@login_required
def my_appointments():
    user_appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return render_template('my_appointments.html', appointments=user_appointments)

@app.route('/save_property/<int:property_id>')
@login_required
def save_property(property_id):
    property = Property.query.get_or_404(property_id)
    saved_property = SavedProperty(user_id=current_user.id, property_id=property_id)
    db.session.add(saved_property)
    db.session.commit()
    flash('Property saved successfully!')
    return redirect(url_for('my_properties'))

@app.route('/unsave_property/<int:property_id>')
@login_required
def unsave_property(property_id):
    saved_property = SavedProperty.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if saved_property:
        db.session.delete(saved_property)
        db.session.commit()
        flash('Property unsaved successfully!')
    return redirect(url_for('my_properties'))

@app.route('/make_inquiry/<int:property_id>', methods=['GET', 'POST'])
@login_required
def make_inquiry(property_id):
    property = Property.query.get_or_404(property_id)
    if request.method == 'POST':
        message = request.form.get('message')
        inquiry = Inquiry(user_id=current_user.id, property_id=property_id, message=message)
        db.session.add(inquiry)
        db.session.commit()
        flash('Inquiry sent successfully!')
        return redirect(url_for('my_inquiries'))
    return render_template('make_inquiry.html', property=property)

@app.route('/book_appointment/<int:property_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(property_id):
    property = Property.query.get_or_404(property_id)
    if request.method == 'POST':
        appointment_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d')
        appointment = Appointment(user_id=current_user.id, property_id=property_id, appointment_date=appointment_date)
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!')
        return redirect(url_for('my_appointments'))
    return render_template('book_appointment.html', property=property)

@app.route('/properties/<int:property_id>/buy', methods=['GET', 'POST'])
@login_required
def buy_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    if property.status != 'available':
        flash('This property is no longer available for purchase.', 'danger')
        return redirect(url_for('view_property', property_id=property_id))
    
    if property.transaction_type != 'sale':
        flash('This property is not for sale.', 'danger')
        return redirect(url_for('view_property', property_id=property_id))
    
    if request.method == 'POST':
        # Create a purchase request record
        purchase_request = PropertyPurchase(
            property_id=property.id,
            user_id=current_user.id,
            status='pending',
            request_date=datetime.utcnow()
        )
        
        try:
            db.session.add(purchase_request)
            db.session.commit()
            flash('Your purchase request has been submitted successfully!', 'success')
            return redirect(url_for('purchase_success', property_id=property.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your request. Please try again.', 'error')
            return redirect(url_for('buy_property', property_id=property_id))
    
    return render_template('buy_property.html', property=property)

@app.route('/purchase_success/<int:property_id>')
@login_required
def purchase_success(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('purchase_success.html', property=property)

# Password Reset Routes
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Here you would typically:
            # 1. Generate a secure token
            # 2. Send reset email
            # For now, we'll just show a success message
            flash('If an account exists with that email, you will receive password reset instructions.', 'info')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Here you would validate the token and get the user
    # For now, we'll just show the reset form
    if request.method == 'POST':
        password = request.form.get('password')
        # Update password logic would go here
        flash('Your password has been reset.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        # For now, we'll just show a success message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Admin Routes
@app.route('/admin/properties/manage')
@login_required
@admin_required
def manage_properties():
    properties = Property.query.all()
    return render_template('admin/manage_properties.html', properties=properties)

@app.route('/admin/properties/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_property():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        property_type = request.form.get('property_type')
        transaction_type = request.form.get('transaction_type')
        price = float(request.form.get('price'))
        area = float(request.form.get('area'))
        bedrooms = int(request.form.get('bedrooms'))
        bathrooms = float(request.form.get('bathrooms'))
        location = request.form.get('location')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        amenities = request.form.get('amenities')
        agent_id = request.form.get('agent_id')
        
        # Create new property
        property = Property(
            title=title,
            description=description,
            property_type=property_type,
            transaction_type=transaction_type,
            price=price,
            area=area,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            location=location,
            address=address,
            city=city,
            state=state,
            zipcode=zipcode,
            amenities=amenities,
            agent_id=agent_id
        )
        
        db.session.add(property)
        db.session.commit()
        
        flash('Property added successfully!', 'success')
        return redirect(url_for('manage_properties'))
    
    agents = User.query.filter_by(role='agent').all()
    return render_template('admin/add_property.html', agents=agents)

@app.route('/admin/properties/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    
    if request.method == 'POST':
        property.title = request.form.get('title')
        property.description = request.form.get('description')
        property.price = float(request.form.get('price'))
        property.location = request.form.get('location')
        property.property_type = request.form.get('property_type')
        property.status = request.form.get('status')
        property.agent_id = request.form.get('agent_id')
        
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('manage_properties'))
    
    agents = User.query.filter_by(role='agent').all()
    return render_template('admin/edit_property.html', property=property, agents=agents)

@app.route('/admin/inquiries')
@login_required
@admin_required
def view_inquiries():
    inquiries = Inquiry.query.all()
    return render_template('admin/inquiries.html', inquiries=inquiries)

@app.route('/admin/appointments')
@login_required
@admin_required
def view_appointments():
    appointments = Appointment.query.all()
    return render_template('admin/appointments.html', appointments=appointments)

@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if current_password and not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('edit_profile'))
        
        # Update email if changed
        if email and email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'danger')
                return redirect(url_for('edit_profile'))
            current_user.email = email
        
        # Update password if provided
        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('edit_profile'))
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_profile.html')

def create_test_users():
    try:
        # Create admin user
        admin = User(
            user_id='DH000001',
            email='admin@dreamhome.com',
            role='admin',
            is_admin=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)

        # Create agent user
        agent = User(
            user_id='DH000002',
            email='agent@dreamhome.com',
            role='agent'
        )
        agent.set_password('Agent@123')
        db.session.add(agent)

        # Create regular user
        user = User(
            user_id='DH000003',
            email='john@example.com',
            role='user'
        )
        user.set_password('User@123')
        db.session.add(user)

        db.session.commit()
        print("Test users created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating test users: {e}")

def create_test_properties():
    # Only create test properties if none exist
    if Property.query.first() is None:
        properties = [
            {
                'title': 'Luxury Beachfront Villa',
                'description': 'Beautiful 4-bedroom villa with direct beach access and stunning ocean views.',
                'property_type': 'house',
                'transaction_type': 'sale',
                'price': 1250000.00,
                'area': 3500,
                'bedrooms': 4,
                'bathrooms': 3.5,
                'location': 'Miami Beach',
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'state': 'Florida',
                'zipcode': '33139',
                'amenities': '["Pool", "Garden", "Garage", "Security System"]',
                'images': '["villa1.jpg", "villa2.jpg", "villa3.jpg"]',
                'featured': True
            },
            {
                'title': 'Modern Downtown Apartment',
                'description': 'Sleek 2-bedroom apartment in the heart of downtown with city views.',
                'property_type': 'apartment',
                'transaction_type': 'rent',
                'price': 2500.00,
                'area': 1200,
                'bedrooms': 2,
                'bathrooms': 2,
                'location': 'Downtown',
                'address': '456 Main Street',
                'city': 'Miami',
                'state': 'Florida',
                'zipcode': '33130',
                'amenities': '["Gym", "Pool", "Parking", "24/7 Security"]',
                'images': '["apt1.jpg", "apt2.jpg"]',
                'featured': True
            },
            {
                'title': 'Commercial Office Space',
                'description': 'Prime location office space perfect for startups or established businesses.',
                'property_type': 'commercial',
                'transaction_type': 'sale',
                'price': 750000.00,
                'area': 2000,
                'bedrooms': 0,
                'bathrooms': 2,
                'location': 'Business District',
                'address': '789 Business Ave',
                'city': 'Miami',
                'state': 'Florida',
                'zipcode': '33131',
                'amenities': '["Parking", "Conference Room", "Kitchen", "Reception Area"]',
                'images': '["office1.jpg", "office2.jpg"]',
                'featured': True
            }
        ]

        for prop_data in properties:
            property = Property(**prop_data)
            db.session.add(property)
        
        db.session.commit()

def init_db():
    with app.app_context():
        db.create_all()
        create_test_users()
        create_test_properties()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
