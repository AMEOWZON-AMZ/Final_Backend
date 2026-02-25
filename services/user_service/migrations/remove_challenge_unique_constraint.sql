-- Migration: Remove UNIQUE constraint to allow multiple submissions per user per challenge
-- Date: 2026-02-25
-- Purpose: Allow users to submit multiple photos for the same daily challenge

-- Remove the UNIQUE constraint on (user_id, challenge_day_id)
ALTER TABLE challenge_submissions 
DROP CONSTRAINT IF EXISTS ux_user_challenge;

-- Verify the constraint is removed
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'challenge_submissions'::regclass;
