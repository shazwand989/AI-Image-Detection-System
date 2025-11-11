"""
Seed database with sample data for demonstration
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import execute_query
import bcrypt

def seed_data():
    """Add sample data to the database"""
    
    print("🌱 Seeding database with sample data...")
    
    # 1. Create sample admin user
    print("\n1️⃣ Creating sample admin user...")
    try:
        admin_exists = execute_query(
            "SELECT id FROM users WHERE username = %s",
            ('admin',),
            fetch_one=True
        )
        
        if not admin_exists:
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            execute_query(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                ('admin', password_hash, 'admin')
            )
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("⚠️  Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    
    # 2. Add sample scam tips
    print("\n2️⃣ Adding sample scam tips...")
    sample_tips = [
        {
            'title': 'Verify Before You Pay - Parcel Delivery Scams',
            'image_path': None
        },
        {
            'title': 'Never Click Suspicious Links in SMS',
            'image_path': None
        },
        {
            'title': 'Official Delivery Services Never Ask for Immediate Payment',
            'image_path': None
        }
    ]
    
    for tip in sample_tips:
        try:
            existing = execute_query(
                "SELECT id FROM scam_tips WHERE title = %s",
                (tip['title'],),
                fetch_one=True
            )
            if not existing:
                execute_query(
                    "INSERT INTO scam_tips (title, image_path) VALUES (%s, %s)",
                    (tip['title'], tip['image_path'])
                )
                print(f"✅ Added: {tip['title']}")
            else:
                print(f"⚠️  Already exists: {tip['title']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 3. Add sample scam cases
    print("\n3️⃣ Adding sample Malaysia scam cases...")
    sample_cases = [
        {
            'headline': 'RM500,000 Lost in Fake Parcel Delivery Scam - Selangor 2024',
            'image_path': None,
            'news_link': 'https://www.thestar.com.my/news/nation'
        },
        {
            'headline': 'Police Warn Against Parcel Scam Using Fake Pos Malaysia SMS',
            'image_path': None,
            'news_link': 'https://www.nst.com.my/news/nation'
        },
        {
            'headline': 'Elderly Woman Loses RM80,000 in Parcel Delivery Scam',
            'image_path': None,
            'news_link': 'https://www.malaymail.com/news/malaysia'
        }
    ]
    
    for case in sample_cases:
        try:
            existing = execute_query(
                "SELECT id FROM malaysia_cases WHERE headline = %s",
                (case['headline'],),
                fetch_one=True
            )
            if not existing:
                execute_query(
                    "INSERT INTO malaysia_cases (headline, image_path, news_link) VALUES (%s, %s, %s)",
                    (case['headline'], case['image_path'], case['news_link'])
                )
                print(f"✅ Added: {case['headline']}")
            else:
                print(f"⚠️  Already exists: {case['headline']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 4. Add sample user manuals
    print("\n4️⃣ Adding sample user manuals...")
    sample_manuals = [
        {
            'title': 'How to Use AI Image Detection System',
            'file_path': None
        },
        {
            'title': 'Guide to Identifying Parcel Scams',
            'file_path': None
        }
    ]
    
    for manual in sample_manuals:
        try:
            existing = execute_query(
                "SELECT id FROM user_manual WHERE title = %s",
                (manual['title'],),
                fetch_one=True
            )
            if not existing:
                execute_query(
                    "INSERT INTO user_manual (title, file_path) VALUES (%s, %s)",
                    (manual['title'], manual['file_path'])
                )
                print(f"✅ Added: {manual['title']}")
            else:
                print(f"⚠️  Already exists: {manual['title']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Database seeding completed!")
    print("\n📝 Sample Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Role: Admin")

if __name__ == '__main__':
    try:
        seed_data()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
