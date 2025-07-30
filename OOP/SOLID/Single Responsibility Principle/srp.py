# Following Adheres to SRP

class User:

    def __init__(self, name, email):
        self.name = name
        self.email = email


class UserRepository:
    def save(self, user):
        print(f"Saving user: {user} to database.")

class EmailService:
    def send_email(self, email, message):
        print(f"Sending email to the user: {email} and message:{message}")

