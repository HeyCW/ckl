-- Adds the audit columns to container_delivery_costs on an existing
-- Postgres database.
--
-- The app performs this same migration itself on every startup (see
-- Database._run_migrations), so running this by hand is only needed when
-- you want the change applied before deploying, or when the app's own
-- ALTER would fail because the tables are not owned by the app's role.
-- That failure is logged as a warning and nothing else, so it is easy to
-- miss - check with:
--     SELECT tablename, tableowner FROM pg_tables
--     WHERE schemaname = 'public' AND tablename = 'container_delivery_costs';
--
-- Run as the role the app connects as (DB_USER, normally ckl_app):
--     psql -h <host> -U ckl_app -d ckl -1 -f scripts/add_audit_delivery_costs.sql
--
-- Safe to re-run: every statement is IF NOT EXISTS or an idempotent
-- SET DEFAULT.
--
-- Existing rows keep NULL in all four columns. There is no way to
-- reconstruct who created a cost that was entered before this ran, so
-- those rows show as "—" in the Biaya Pengantaran table forever.

ALTER TABLE container_delivery_costs ADD COLUMN IF NOT EXISTS created_by TEXT;
ALTER TABLE container_delivery_costs ADD COLUMN IF NOT EXISTS edited_by  TEXT;
ALTER TABLE container_delivery_costs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;
ALTER TABLE container_delivery_costs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;

-- Attached separately rather than in ADD COLUMN so this file stays in
-- step with the app's own migration, which has to add the columns bare:
-- SQLite's ALTER TABLE rejects a non-constant DEFAULT.
ALTER TABLE container_delivery_costs ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE container_delivery_costs ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP;

-- Check what landed.
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'container_delivery_costs'
  AND column_name IN ('created_by', 'edited_by', 'created_at', 'updated_at')
ORDER BY column_name;
