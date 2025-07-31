from abc import ABC, abstractmethod

# Violates DIP: High-level module depends on concrete low-level module
class SQLDatabase:
    def save(self, data):
        print(f"Saving {data} to SQL database")

class UserService:
    def __init__(self):
        self.databse = SQLDatabase() # Direct dependency
    
    def save_user(self, user):
        self.database.save(user)

# Adheres to DIP: Depend on abstraction
class Database(ABC):
    @abstractmethod
    def save(self, data):
        pass

class SQLDatabase(Database):
    def save(self, data):
        print(f"Saving {data} to SQL database")

class MongoDatabse(Database):
    def save(self, data):
        print(f"Saving {data} to MongoDB")


class UserService:
    def __init__(self, database: Database):
        self.database = database

    def save_user(self, user):
        self.database.save(user)
        