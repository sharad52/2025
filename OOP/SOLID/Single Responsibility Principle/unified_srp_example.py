# Violates Single Responsibility Principle.

class UserManager:
    
    def __init__(self):
        self.users = []

    def add_user(self, name, email):
        # Responsibility 1 => User management
        user = {'name': name, 'email': email}
        self.users.append(user)
    
    def send_welcome_email(self, user):
        # Responsibility 2 => Email handling
        print(f"Sending welcome email to: {user.get('email')}")
        # Email handling logic here
    
    def save_to_database(self, user):
        # Responsibility 3 => Data persistence
        print(f"Saving user: {user['email']} to database.")
        # Database logic here.
    
    def generate_user_report(self):
        # Responsibility 4 => Report generation
        report = 'User Report:\n'
        for user in self.users:
            report += f"- User Name:{user['name']} Email: {user['email']}\n"
        return report
    

# Example adhering to the SRP

class User:
    """Represents a User entity - Single Responsibility: User data management"""
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def get_info(self):
        return {'name': self.name, 'email': self.email}

class UserRepository:
    """Handles User data persistence - Single Responsibility: Data Storage"""
    def __init__(self):
        self.users = []

    def save(self, user):
        self.users.append(user)
        print(f"Saving user to the db")

    def find_all(self):
        return self.users
    

class EmailService:
    """handles email operations - Single responsibility: Email communication"""
    def send_welcome_email(self, user):
        print(f"Sending welcome email to {user.email}")
        # Email sending logic here
    

class UserReportGenerator:
    """Generates user reports - Single responsibility: Report generation"""
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    def generate_report(self):
        users = self.user_repository.find_all()
        report = "User Report:\n"
        for user in users:
            report += f"- {user.name} ({user.email})\n"
        return report


class UserService:
    """Orchestrates user operations - Single Responsibility: User workflow coordination"""
    def __init__(self, user_repository, email_service):
        self.user_repository = user_repository
        self.email_service = email_service

    def register_user(self, name, email):
        user = User(name, email)
        self.user_repository.save(user)
        self.email_service.send_welcome_email(user)
        return user
    
