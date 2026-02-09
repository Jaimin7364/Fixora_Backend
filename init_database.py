"""
Database Initialization Script for Fixora

This script initializes the database with:
1. Default SLA policies  
2. Sample users
3. Sample knowledge base articles

Run this after deploying the backend for the first time.

Usage:
    python init_database.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.sla_policy import SLAPolicy
from app.models.user import User, UserRole
from app.models.ticket import TicketPriority
from app.models.knowledge_base import KnowledgeBase


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


def init_sla_policies(db: Session):
    """Initialize default SLA policies"""
    print("\nInitializing SLA policies...")
    
    # Check if SLA policies already exist
    existing = db.query(SLAPolicy).first()
    if existing:
        print("⚠️  SLA policies already exist, skipping...")
        return
    
    sla_policies = [
        SLAPolicy(
            priority=TicketPriority.LOW,
            response_time_hours=24,
            resolution_time_hours=72,
            description="Low priority - 3 business days resolution"
        ),
        SLAPolicy(
            priority=TicketPriority.MEDIUM,
            response_time_hours=8,
            resolution_time_hours=48,
            description="Medium priority - 2 business days resolution"
        ),
        SLAPolicy(
            priority=TicketPriority.HIGH,
            response_time_hours=4,
            resolution_time_hours=24,
            description="High priority - 24 hours resolution"
        ),
        SLAPolicy(
            priority=TicketPriority.URGENT,
            response_time_hours=1,
            resolution_time_hours=8,
            description="Urgent priority - 8 hours resolution"
        )
    ]
    
    for policy in sla_policies:
        db.add(policy)
    
    db.commit()
    print("✅ SLA policies created:")
    print("   - Low: 72 hours")
    print("   - Medium: 48 hours")
    print("   - High: 24 hours")
    print("   - Urgent: 8 hours")


def init_sample_users(db: Session):
    """Create sample users"""
    print("\nCreating sample users...")
    
    # Check if users already exist
    existing = db.query(User).first()
    if existing:
        print("⚠️  Users already exist, skipping...")
        return
    
    users = [
        User(
            email="admin@fixora.com",
            full_name="Admin User",
            department="IT",
            role=UserRole.ADMIN,
            phone="+1-555-0001",
            is_active=True
        ),
        User(
            email="support@fixora.com",
            full_name="IT Support",
            department="IT",
            role=UserRole.IT_SUPPORT,
            phone="+1-555-0002",
            is_active=True
        ),
        User(
            email="john.doe@fixora.com",
            full_name="John Doe",
            department="Engineering",
            role=UserRole.EMPLOYEE,
            phone="+1-555-0101",
            is_active=True
        ),
        User(
            email="jane.smith@fixora.com",
            full_name="Jane Smith",
            department="Marketing",
            role=UserRole.EMPLOYEE,
            phone="+1-555-0102",
            is_active=True
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.commit()
    print("✅ Sample users created:")
    print("   - admin@fixora.com (Admin)")
    print("   - support@fixora.com (IT Support)")
    print("   - john.doe@fixora.com (Employee)")
    print("   - jane.smith@fixora.com (Employee)")


def init_knowledge_base(db: Session):
    """Create sample knowledge base articles"""
    print("\nCreating sample KB articles...")
    
    # Check if KB articles already exist
    existing = db.query(KnowledgeBase).first()
    if existing:
        print("⚠️  KB articles already exist, skipping...")
        return
    
    articles = [
        KnowledgeBase(
            title="How to reset your password",
            question="I forgot my password, how do I reset it?",
            answer="1. Go to login page\n2. Click 'Forgot Password'\n3. Enter your email\n4. Check your email for reset link\n5. Click link and create new password",
            category="account",
            keywords="password, reset, forgot, login",
            is_featured=True
        ),
        KnowledgeBase(
            title="Printer offline troubleshooting",
            question="My printer shows as offline, what should I do?",
            answer="1. Check if printer is powered on\n2. Verify USB or network cable connection\n3. Restart Print Spooler service\n4. Set printer as default\n5. Try printing a test page",
            category="printer",
            keywords="printer, offline, not printing, connection",
            is_featured=True
        ),
        KnowledgeBase(
            title="VPN connection setup",
            question="How do I connect to company VPN?",
            answer="1. Open VPN client\n2. Enter VPN server address\n3. Use your company credentials\n4. Select 'Save credentials'\n5. Click Connect",
            category="network",
            keywords="vpn, remote access, connection",
            is_featured=False
        ),
        KnowledgeBase(
            title="Software installation request",
            question="How do I request new software installation?",
            answer="1. Create a ticket with software name\n2. Provide business justification\n3. Include manager approval\n4. IT will review within 2 business days",
            category="software",
            keywords="software, install, request, application",
            is_featured=False
        )
    ]
    
    for article in articles:
        db.add(article)
    
    db.commit()
    print("✅ Knowledge base articles created")
    print(f"   - {len(articles)} articles added")


def main():
    """Main initialization function"""
    print("="*50)
    print("Fixora Database Initialization")
    print("="*50)
    
    try:
        # Create tables
        create_tables()
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Initialize data
            init_sla_policies(db)
            init_sample_users(db)
            init_knowledge_base(db)
            
            print("\n" + "="*50)
            print("✅ Database initialization completed successfully!")
            print("="*50)
            print("\nYou can now:")
            print("1. Create tickets via API")
            print("2. Test n8n integration")
            print("3. Connect Slack bot")
            print("\nAPI Documentation: http://your-server:8000/docs")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
