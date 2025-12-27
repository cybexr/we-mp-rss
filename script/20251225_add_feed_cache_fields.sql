-- ============================================================================
-- Migration: Add cache_images, remarks, category fields to feeds table
-- Purpose: Add support for image caching control, user remarks, and feed categorization
-- Author: System Migration
-- Date: 2025-12-25
-- ============================================================================
--
-- This migration adds three new columns to the feeds table:
-- 1. cache_images (BOOLEAN/TINYINT) - Enable/disable image caching during content extraction
-- 2. remarks (VARCHAR(255)) - User remarks for this feed
-- 3. category (VARCHAR(255)) - Feed category for grouping and filtering
--
-- Database Compatibility: MySQL 5.7+ / SQLite 3.x
--
-- ============================================================================

-- ============================================================================
-- Migration UP (Apply Changes)
-- ============================================================================

-- Add cache_images column (BOOLEAN/TINYINT with default FALSE/0)
-- Purpose: Control whether images should be cached during content extraction
ALTER TABLE feeds ADD COLUMN cache_images BOOLEAN DEFAULT 0;

-- Add remarks column (VARCHAR(255) with default empty string)
-- Purpose: Allow users to add notes or remarks for specific feeds
ALTER TABLE feeds ADD COLUMN remarks VARCHAR(255) DEFAULT '';

-- Add category column (VARCHAR(255) with default empty string)
-- Purpose: Categorize feeds for better organization and filtering
ALTER TABLE feeds ADD COLUMN category VARCHAR(255) DEFAULT '';

-- ============================================================================
-- Migration DOWN (ROLLBACK - WARNING: This will permanently delete data)
-- ============================================================================

-- WARNING: Rolling back this migration will permanently delete all data in these columns!
-- Ensure you have backed up your database before executing ROLLBACK section.

-- Drop cache_images column
ALTER TABLE feeds DROP COLUMN cache_images;

-- Drop remarks column
ALTER TABLE feeds DROP COLUMN remarks;

-- Drop category column
ALTER TABLE feeds DROP COLUMN category;

-- ============================================================================
-- Usage Instructions
-- ============================================================================
--
-- APPLY MIGRATION:
--
-- For MySQL:
--   mysql -u username -p database_name < 20251225_add_feed_cache_fields.sql
--   OR inside mysql client:
--   source /path/to/20251225_add_feed_cache_fields.sql
--
-- For SQLite:
--   sqlite3 database.db < 20251225_add_feed_cache_fields.sql
--   OR inside sqlite client:
--   .read /path/to/20251225_add_feed_cache_fields.sql
--
-- ROLLBACK MIGRATION:
--   WARNING: ROLLBACK will permanently delete all data in these columns!
--   1. Backup your database before rolling back
--   2. Execute only the DOWN section (ROLLBACK) commands manually
--   3. For MySQL: Execute DROP COLUMN statements above
--   4. For SQLite: SQLite does NOT support DROP COLUMN in ALTER TABLE
--      You must recreate the table without the dropped columns
--
-- IMPORTANT NOTES:
--   - This script is for PRODUCTION databases with existing data
--   - Development databases will auto-create these columns on restart via create_all()
--   - Always backup your database before applying migrations
--   - Test this migration on a staging database first
--   - For SQLite DROP COLUMN limitations, consider exporting data, recreating schema, and reimporting
--
-- ============================================================================
