-- Creates a non-superuser role and database for the app to connect as.
--
-- Run this once, as an existing Postgres superuser, on the VPS:
--   psql -U postgres -f scripts/postgres_setup.sql
--
-- Then set DB_USER/DB_PASSWORD/DB_NAME in .env to match what you choose
-- below. Never point DB_USER at the "postgres" superuser role for normal
-- app traffic - it can read/write every database on the server,
-- create/drop other roles and databases, and bypass row-level security.
-- This role can only do those things inside its own database.

-- 1. Change this password before running, or edit it in psql afterwards
--    with: ALTER ROLE ckl_app WITH PASSWORD 'something-else';
CREATE ROLE ckl_app WITH LOGIN PASSWORD 'CHANGE_ME' NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

-- 2. A database owned by that role. Ownership (rather than just
--    per-table GRANTs) is what lets the app's own init_db()/migration
--    logic create and alter its tables on first run and on upgrades,
--    without needing a superuser to intervene each time - while still
--    confining that privilege to this one database.
CREATE DATABASE ckl OWNER ckl_app;

-- 3. Postgres 15+ already revokes CREATE on the public schema from
--    PUBLIC by default; this makes sure of it on older versions too, so
--    only ckl_app (as owner) can create objects in this database.
\connect ckl
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
