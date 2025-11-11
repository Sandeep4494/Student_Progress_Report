"""
Script to seed the database
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Import and run seed
if __name__ == "__main__":
    from db.seed import seed_database
    seed_database()


