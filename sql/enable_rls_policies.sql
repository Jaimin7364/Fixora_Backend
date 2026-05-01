-- Enable PostgreSQL row-level security for tenant isolation.
-- Run this after organization_id is fully backfilled.

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_memberships ENABLE ROW LEVEL SECURITY;

-- Optional: force RLS so table owners are also subject to policies.
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE tickets FORCE ROW LEVEL SECURITY;
ALTER TABLE ticket_activities FORCE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base FORCE ROW LEVEL SECURITY;
ALTER TABLE attachments FORCE ROW LEVEL SECURITY;
ALTER TABLE sla_policies FORCE ROW LEVEL SECURITY;
ALTER TABLE organization_memberships FORCE ROW LEVEL SECURITY;

-- App must set: SET app.current_organization_id = '<org_id>' per DB session.

DROP POLICY IF EXISTS users_tenant_isolation ON users;
CREATE POLICY users_tenant_isolation ON users
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS tickets_tenant_isolation ON tickets;
CREATE POLICY tickets_tenant_isolation ON tickets
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS ticket_activities_tenant_isolation ON ticket_activities;
CREATE POLICY ticket_activities_tenant_isolation ON ticket_activities
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS kb_tenant_isolation ON knowledge_base;
CREATE POLICY kb_tenant_isolation ON knowledge_base
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS attachments_tenant_isolation ON attachments;
CREATE POLICY attachments_tenant_isolation ON attachments
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS sla_tenant_isolation ON sla_policies;
CREATE POLICY sla_tenant_isolation ON sla_policies
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);

DROP POLICY IF EXISTS memberships_tenant_isolation ON organization_memberships;
CREATE POLICY memberships_tenant_isolation ON organization_memberships
USING (organization_id = current_setting('app.current_organization_id', true)::int)
WITH CHECK (organization_id = current_setting('app.current_organization_id', true)::int);
