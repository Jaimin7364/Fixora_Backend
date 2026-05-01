"""
Setup script to create 2 test organizations with admin users.

Usage:
    python test_setup_tenants.py

This will create:
- Organization Alpha + admin user (alpha_admin@test.com)
- Organization Beta + admin user (beta_admin@test.com)

Then print login tokens for testing.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.models.user import User, UserRole
from app.services.user_service import UserService


def setup_tenants() -> None:
    """Create 2 organizations with admin users"""
    print("Creating test organizations...")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if already set up
        alpha_org = db.query(Organization).filter(Organization.slug == "alpha").first()
        beta_org = db.query(Organization).filter(Organization.slug == "beta").first()
        
        if alpha_org and beta_org:
            print("✅ Organizations already exist. Skipping creation.")
            alpha_admin = db.query(User).filter(User.email == "alpha_admin@test.com").first()
            beta_admin = db.query(User).filter(User.email == "beta_admin@test.com").first()
        else:
            # Create Organization Alpha
            alpha_org = Organization(name="Alpha Corp", slug="alpha", is_active=True)
            db.add(alpha_org)
            db.commit()
            db.refresh(alpha_org)
            print(f"✅ Created Organization: {alpha_org.name} (id={alpha_org.id})")
            
            # Create Organization Beta
            beta_org = Organization(name="Beta Industries", slug="beta", is_active=True)
            db.add(beta_org)
            db.commit()
            db.refresh(beta_org)
            print(f"✅ Created Organization: {beta_org.name} (id={beta_org.id})")
            
            # Create Admin for Alpha
            alpha_admin = UserService.create_user(
                db,
                type('UserCreate', (), {
                    'email': 'alpha_admin@test.com',
                    'full_name': 'Alpha Admin',
                    'password': 'TestPassword123',
                    'department': 'IT',
                    'phone': '+1-555-0001',
                    'role': UserRole.ADMIN,
                    'teams_user_id': None,
                    'organization_id': None,
                })(),
                alpha_org.id
            )
            print(f"✅ Created user: {alpha_admin.email} in {alpha_org.name}")
            
            # Create Admin for Beta
            beta_admin = UserService.create_user(
                db,
                type('UserCreate', (), {
                    'email': 'beta_admin@test.com',
                    'full_name': 'Beta Admin',
                    'password': 'TestPassword123',
                    'department': 'IT',
                    'phone': '+1-555-0002',
                    'role': UserRole.ADMIN,
                    'teams_user_id': None,
                    'organization_id': None,
                })(),
                beta_org.id
            )
            print(f"✅ Created user: {beta_admin.email} in {beta_org.name}")
        
        print("\n" + "="*60)
        print("TEST CREDENTIALS")
        print("="*60)
        print(f"\nOrganization Alpha (id={alpha_org.id})")
        print(f"  Email: alpha_admin@test.com")
        print(f"  Password: TestPassword123")
        print(f"  Role: admin")
        
        print(f"\nOrganization Beta (id={beta_org.id})")
        print(f"  Email: beta_admin@test.com")
        print(f"  Password: TestPassword123")
        print(f"  Role: admin")
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Start backend server:")
        print("   uvicorn app.main:app --reload")
        
        print("\n2. Login Alpha admin and get token:")
        print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
        print("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("     -d 'username=alpha_admin@test.com&password=TestPassword123'")
        
        print("\n3. Login Beta admin and get token:")
        print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
        print("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("     -d 'username=beta_admin@test.com&password=TestPassword123'")
        
        print("\n4. Then run isolation tests (see test_tenant_isolation.sh)")
        print("="*60)
        
    finally:
        db.close()


if __name__ == "__main__":
    setup_tenants()
