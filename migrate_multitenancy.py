"""
Backfill script for multi-tenant rollout.

What it does:
1. Ensures the new organization tables/columns exist.
2. Creates a default organization when missing.
3. Backfills organization_id across existing records.
4. Creates organization_membership rows for users.

Usage:
    python migrate_multitenancy.py
"""

import os
import sys

from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base  # noqa: E402
from app.database.session import SessionLocal, engine  # noqa: E402
from app.models.attachment import Attachment  # noqa: E402
from app.models.knowledge_base import KnowledgeBase  # noqa: E402
from app.models.organization import Organization  # noqa: E402
from app.models.organization_membership import OrganizationMembership  # noqa: E402
from app.models.sla_policy import SLAPolicy  # noqa: E402
from app.models.ticket import Ticket  # noqa: E402
from app.models.ticket_activity import TicketActivity  # noqa: E402
from app.models.user import User  # noqa: E402


DEFAULT_ORG_NAME = "Default Organization"
DEFAULT_ORG_SLUG = "default-organization"


def ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_or_create_default_org(db: Session) -> Organization:
    org = db.query(Organization).filter(Organization.slug == DEFAULT_ORG_SLUG).first()
    if org:
        return org

    org = Organization(name=DEFAULT_ORG_NAME, slug=DEFAULT_ORG_SLUG, is_active=True)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def backfill_users_and_memberships(db: Session, default_org_id: int) -> tuple[int, int]:
    users_updated = 0
    memberships_created = 0

    users = db.query(User).all()
    for user in users:
        if user.organization_id is None:
            user.organization_id = default_org_id
            users_updated += 1

    db.commit()

    for user in users:
        membership = db.query(OrganizationMembership).filter(
            OrganizationMembership.organization_id == user.organization_id,
            OrganizationMembership.user_id == user.id,
        ).first()
        if not membership:
            db.add(
                OrganizationMembership(
                    organization_id=user.organization_id,
                    user_id=user.id,
                    role=user.role.value,
                )
            )
            memberships_created += 1

    db.commit()
    return users_updated, memberships_created


def backfill_tickets(db: Session, default_org_id: int) -> int:
    updated = 0
    tickets = db.query(Ticket).all()
    for ticket in tickets:
        if ticket.organization_id is None:
            if ticket.user and ticket.user.organization_id is not None:
                ticket.organization_id = ticket.user.organization_id
            else:
                ticket.organization_id = default_org_id
            updated += 1
    db.commit()
    return updated


def backfill_ticket_activities(db: Session, default_org_id: int) -> int:
    updated = 0
    activities = db.query(TicketActivity).all()
    for activity in activities:
        if activity.organization_id is None:
            if activity.ticket and activity.ticket.organization_id is not None:
                activity.organization_id = activity.ticket.organization_id
            else:
                activity.organization_id = default_org_id
            updated += 1
    db.commit()
    return updated


def backfill_knowledge_base(db: Session, default_org_id: int) -> int:
    updated = 0
    articles = db.query(KnowledgeBase).filter(KnowledgeBase.organization_id.is_(None)).all()
    for article in articles:
        article.organization_id = default_org_id
        updated += 1
    db.commit()
    return updated


def backfill_attachments(db: Session, default_org_id: int) -> int:
    updated = 0
    attachments = db.query(Attachment).all()
    for attachment in attachments:
        if attachment.organization_id is None:
            if attachment.ticket and attachment.ticket.organization_id is not None:
                attachment.organization_id = attachment.ticket.organization_id
            else:
                attachment.organization_id = default_org_id
            updated += 1
    db.commit()
    return updated


def backfill_sla_policies(db: Session, default_org_id: int) -> int:
    updated = 0
    policies = db.query(SLAPolicy).filter(SLAPolicy.organization_id.is_(None)).all()
    for policy in policies:
        policy.organization_id = default_org_id
        updated += 1
    db.commit()
    return updated


def main() -> None:
    print("Running multi-tenant backfill migration...")
    ensure_tables()

    db = SessionLocal()
    try:
        default_org = get_or_create_default_org(db)

        users_updated, memberships_created = backfill_users_and_memberships(db, default_org.id)
        tickets_updated = backfill_tickets(db, default_org.id)
        activities_updated = backfill_ticket_activities(db, default_org.id)
        kb_updated = backfill_knowledge_base(db, default_org.id)
        attachments_updated = backfill_attachments(db, default_org.id)
        sla_updated = backfill_sla_policies(db, default_org.id)

        print("Migration complete:")
        print(f"  users updated: {users_updated}")
        print(f"  memberships created: {memberships_created}")
        print(f"  tickets updated: {tickets_updated}")
        print(f"  ticket activities updated: {activities_updated}")
        print(f"  knowledge base updated: {kb_updated}")
        print(f"  attachments updated: {attachments_updated}")
        print(f"  sla policies updated: {sla_updated}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
