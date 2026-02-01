"""
Initialize database with default SLA policies and sample data

Run this script after starting the server for the first time to populate
the database with initial data.

Usage:
    python init_db.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def create_sample_users():
    """Create sample users"""
    print("Creating sample users...")
    
    users = [
        {
            "email": "admin@fixora.com",
            "full_name": "Admin User",
            "department": "IT",
            "role": "admin",
            "phone": "+1-555-0001"
        },
        {
            "email": "support@fixora.com",
            "full_name": "IT Support",
            "department": "IT",
            "role": "it_support",
            "phone": "+1-555-0002"
        },
        {
            "email": "john.doe@fixora.com",
            "full_name": "John Doe",
            "department": "Engineering",
            "role": "employee",
            "phone": "+1-555-0101"
        },
        {
            "email": "jane.smith@fixora.com",
            "full_name": "Jane Smith",
            "department": "Marketing",
            "role": "employee",
            "phone": "+1-555-0102"
        }
    ]
    
    for user in users:
        try:
            response = requests.post(f"{BASE_URL}/users/", json=user)
            if response.status_code == 201:
                print(f"  ✅ Created user: {user['email']}")
            else:
                print(f"  ⚠️  User {user['email']} may already exist")
        except Exception as e:
            print(f"  ❌ Error creating user: {e}")


def create_sample_kb_articles():
    """Create sample knowledge base articles"""
    print("\nCreating sample KB articles...")
    
    articles = [
        {
            "title": "How to reset your password",
            "question": "I forgot my password, how do I reset it?",
            "answer": "1. Go to login page\n2. Click 'Forgot Password'\n3. Enter your email\n4. Check your email for reset link\n5. Click link and create new password",
            "category": "account",
            "keywords": "password, reset, forgot, login",
            "is_featured": True
        },
        {
            "title": "Printer offline troubleshooting",
            "question": "My printer shows as offline, what should I do?",
            "answer": "1. Check if printer is powered on\n2. Verify USB or network cable connection\n3. Restart Print Spooler service:\n   - Press Win+R, type 'services.msc'\n   - Find 'Print Spooler'\n   - Right-click and select 'Restart'\n4. Set printer as default\n5. Try printing a test page",
            "category": "printer",
            "keywords": "printer, offline, not printing, connection",
            "is_featured": True
        },
        {
            "title": "VPN connection setup",
            "question": "How do I connect to company VPN?",
            "answer": "1. Open VPN client\n2. Enter VPN server address: vpn.company.com\n3. Use your company credentials\n4. Select 'Save credentials' for future use\n5. Click Connect\n\nIf issues persist, contact IT support.",
            "category": "network",
            "keywords": "vpn, remote access, connection",
            "is_featured": False
        },
        {
            "title": "Software installation request",
            "question": "How do I request new software installation?",
            "answer": "1. Create a ticket with software name and version\n2. Provide business justification\n3. Include department manager approval\n4. IT will review and approve within 2 business days\n5. Installation will be scheduled",
            "category": "software",
            "keywords": "software, install, request, application",
            "is_featured": False
        },
        {
            "title": "Email not syncing on mobile",
            "question": "My work email is not syncing on my phone",
            "answer": "1. Check internet connection\n2. Verify email settings:\n   - Server: mail.company.com\n   - Port: 993 (IMAP) or 465 (SMTP)\n   - SSL: Enabled\n3. Remove and re-add email account\n4. Ensure mobile device is authorized\n5. Contact IT if issue persists",
            "category": "email",
            "keywords": "email, mobile, sync, phone, not working",
            "is_featured": True
        }
    ]
    
    for article in articles:
        try:
            response = requests.post(f"{BASE_URL}/kb/", json=article)
            if response.status_code == 201:
                print(f"  ✅ Created article: {article['title']}")
            else:
                print(f"  ⚠️  Article may already exist: {article['title']}")
        except Exception as e:
            print(f"  ❌ Error creating article: {e}")


def create_sample_tickets():
    """Create sample tickets"""
    print("\nCreating sample tickets...")
    
    tickets = [
        {
            "title": "Laptop screen flickering",
            "description": "My laptop screen has been flickering since this morning after Windows update. It's making it hard to work.",
            "category": "hardware",
            "user_id": 3
        },
        {
            "title": "Cannot access shared drive",
            "description": "I'm getting 'Access Denied' error when trying to open the Marketing shared drive. I need access urgently for a client presentation.",
            "category": "access",
            "user_id": 4
        },
        {
            "title": "Outlook keeps crashing",
            "description": "Outlook crashes every time I try to send an email with attachments larger than 5MB.",
            "category": "email",
            "user_id": 3
        },
        {
            "title": "Internet connection very slow",
            "description": "Internet speed has been extremely slow for the past 2 days. Pages take forever to load.",
            "category": "network",
            "user_id": 4
        },
        {
            "title": "Request Adobe Creative Cloud license",
            "description": "I need Adobe Creative Cloud for design work. Manager has approved.",
            "category": "software",
            "user_id": 4
        }
    ]
    
    for ticket in tickets:
        try:
            response = requests.post(f"{BASE_URL}/tickets/", json=ticket)
            if response.status_code == 201:
                result = response.json()
                print(f"  ✅ Created ticket: {result.get('ticket_number')} - {ticket['title']}")
            else:
                print(f"  ❌ Error creating ticket: {ticket['title']}")
        except Exception as e:
            print(f"  ❌ Error creating ticket: {e}")


def main():
    print("=" * 60)
    print("Fixora Database Initialization")
    print("=" * 60)
    print("\nThis script will populate the database with sample data:")
    print("  - Users (admin, IT support, employees)")
    print("  - Knowledge base articles")
    print("  - Sample tickets")
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code != 200:
            print("❌ Server is not running!")
            print("Please start the server first: uvicorn app.main:app --reload")
            return
    except Exception as e:
        print("❌ Cannot connect to server!")
        print("Please start the server first: uvicorn app.main:app --reload")
        print(f"Error: {e}")
        print()
        input("Press Enter to exit...")
        return
    
    print("✅ Server is running\n")
    
    # Create sample data
    create_sample_users()
    create_sample_kb_articles()
    create_sample_tickets()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  - View API docs: http://localhost:8000/docs")
    print("  - View tickets: http://localhost:8000/api/v1/tickets/")
    print("  - View KB articles: http://localhost:8000/api/v1/kb/")
    print("  - View metrics: http://localhost:8000/api/v1/metrics/dashboard")
    print()


if __name__ == "__main__":
    main()
