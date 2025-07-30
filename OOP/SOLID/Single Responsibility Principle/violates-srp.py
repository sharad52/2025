# Violates SRP because User Class handle both user data and email sending

class User:
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def save_to_database(self):
        print(f"Saving {self.name} to database")
    
    def send_email(self, message):
        print(f"Sending email to {self.email}, Message: {message}")