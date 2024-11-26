from app import app, db, User, Property, Inquiry, Appointment, bcrypt
from datetime import datetime, timedelta

def init_db():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        # Create all tables
        db.create_all()

        # Create admin user
        admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=admin_password,
            is_admin=True,
            phone='123-456-7890'
        )
        db.session.add(admin)

        # Create some agent users
        agents = [
            {
                'username': 'agent1',
                'email': 'agent1@example.com',
                'password': 'agent123',
                'phone': '111-222-3333'
            },
            {
                'username': 'agent2',
                'email': 'agent2@example.com',
                'password': 'agent123',
                'phone': '444-555-6666'
            }
        ]

        for agent_data in agents:
            password = bcrypt.generate_password_hash(agent_data['password']).decode('utf-8')
            agent = User(
                username=agent_data['username'],
                email=agent_data['email'],
                password_hash=password,
                is_agent=True,
                phone=agent_data['phone']
            )
            db.session.add(agent)

        # Commit to get IDs for the users
        db.session.commit()

        # Get the first agent's ID for sample properties
        agent = User.query.filter_by(username='agent1').first()

        # Create sample properties
        sample_properties = [
            {
                'title': 'Modern Downtown Apartment',
                'description': 'Beautiful modern apartment in the heart of downtown',
                'property_type': 'apartment',
                'transaction_type': 'sale',
                'price': 450000,
                'area': 1200,
                'bedrooms': 2,
                'bathrooms': 2,
                'location': 'Downtown',
                'address': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10001',
                'amenities': '["Parking", "Pool", "Gym"]',
                'images': '["image1.jpg", "image2.jpg"]',
                'status': 'available',
                'featured': True,
                'agent_id': agent.id
            },
            {
                'title': 'Suburban Family Home',
                'description': 'Spacious family home with large backyard',
                'property_type': 'house',
                'transaction_type': 'sale',
                'price': 750000,
                'area': 2500,
                'bedrooms': 4,
                'bathrooms': 3,
                'location': 'Suburbs',
                'address': '456 Oak Ave',
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10002',
                'amenities': '["Garage", "Garden", "Fireplace"]',
                'images': '["image3.jpg", "image4.jpg"]',
                'status': 'available',
                'featured': True,
                'agent_id': agent.id
            },
            {
                'title': 'Commercial Office Space',
                'description': 'Prime location office space',
                'property_type': 'commercial',
                'transaction_type': 'rent',
                'price': 5000,
                'area': 3000,
                'bedrooms': 0,
                'bathrooms': 2,
                'location': 'Business District',
                'address': '789 Business Ave',
                'city': 'New York',
                'state': 'NY',
                'zipcode': '10003',
                'amenities': '["Reception", "Conference Room", "Kitchen"]',
                'images': '["image5.jpg", "image6.jpg"]',
                'status': 'available',
                'featured': False,
                'agent_id': agent.id
            }
        ]

        for prop_data in sample_properties:
            property = Property(**prop_data)
            db.session.add(property)

        # Create some sample users
        sample_users = [
            {
                'username': 'user1',
                'email': 'user1@example.com',
                'password': 'user123',
                'phone': '777-888-9999'
            },
            {
                'username': 'user2',
                'email': 'user2@example.com',
                'password': 'user123',
                'phone': '000-111-2222'
            }
        ]

        for user_data in sample_users:
            password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=password,
                phone=user_data['phone']
            )
            db.session.add(user)

        # Commit all changes
        db.session.commit()

        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
