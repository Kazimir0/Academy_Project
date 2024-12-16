from sqlalchemy.orm import Session
from database import SessionLocal, User
from passlib.context import CryptContext

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Script to hash existing plaintext passwords
def migrate_plaintext_passwords():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()  # Retrieve all users from the database
        for user in users:
            if not user.password.startswith("$2b$"):  # Check if the password is already hashed
                print(f"Hashing password for user: {user.username}")
                hashed_password = hash_password(user.password)  # Hash the password
                user.password = hashed_password  # Update the password in the database with the hashed one
                db.add(user)
        db.commit()
        print("Passwords migrated successfully!")
    except Exception as e:
        print(f"Error during password migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_plaintext_passwords()
