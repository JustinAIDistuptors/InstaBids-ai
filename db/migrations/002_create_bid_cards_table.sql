-- Migration: Create bid_cards table
-- This migration creates the bid_cards table with detailed classification fields.

-- Ensure pgcrypto is available for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS bid_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    primary_category TEXT NOT NULL,
    primary_job_type TEXT NOT NULL,
    primary_ai_confidence FLOAT,
    
    secondary_category TEXT,
    secondary_job_type TEXT,
    secondary_ai_confidence FLOAT,
    
    tertiary_category TEXT,
    tertiary_job_type TEXT,
    tertiary_ai_confidence FLOAT,
    
    classification_details JSONB, -- For storing raw classifier output or reasoning
    
    budget_range TEXT,
    timeline TEXT,
    photo_meta JSONB, -- Storing list of photo metadata dictionaries
    
    status TEXT NOT NULL CHECK (status IN ('draft', 'final', 'pending_review', 'sent_to_contractors', 'archived')),
    
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    CONSTRAINT bid_cards_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects(id) ON DELETE CASCADE
);

COMMENT ON TABLE bid_cards IS 'Stores generated bid cards with detailed AI classifications for projects';
COMMENT ON COLUMN bid_cards.id IS 'Unique identifier for the bid card';
COMMENT ON COLUMN bid_cards.project_id IS 'Reference to the project this bid card belongs to';
COMMENT ON COLUMN bid_cards.primary_category IS 'Primary classified category for the project';
COMMENT ON COLUMN bid_cards.primary_job_type IS 'Primary classified job type for the project';
COMMENT ON COLUMN bid_cards.primary_ai_confidence IS 'AI confidence score for the primary classification';
COMMENT ON COLUMN bid_cards.secondary_category IS 'Secondary classified category (optional)';
COMMENT ON COLUMN bid_cards.secondary_job_type IS 'Secondary classified job type (optional)';
COMMENT ON COLUMN bid_cards.secondary_ai_confidence IS 'AI confidence score for the secondary classification (optional)';
COMMENT ON COLUMN bid_cards.tertiary_category IS 'Tertiary classified category (optional)';
COMMENT ON COLUMN bid_cards.tertiary_job_type IS 'Tertiary classified job type (optional)';
COMMENT ON COLUMN bid_cards.tertiary_ai_confidence IS 'AI confidence score for the tertiary classification (optional)';
COMMENT ON COLUMN bid_cards.classification_details IS 'Detailed output or reasoning from the classification process (JSONB)';
COMMENT ON COLUMN bid_cards.budget_range IS 'Estimated budget range for the project';
COMMENT ON COLUMN bid_cards.timeline IS 'Desired project timeline';
COMMENT ON COLUMN bid_cards.photo_meta IS 'Metadata from vision analysis of project photos (list of dicts as JSONB)';
COMMENT ON COLUMN bid_cards.status IS 'Current status of the bid card';
COMMENT ON COLUMN bid_cards.inserted_at IS 'Timestamp when the bid card was created';
COMMENT ON COLUMN bid_cards.updated_at IS 'Timestamp when the bid card was last updated';

-- Create indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS bid_cards_project_id_idx ON bid_cards(project_id);
CREATE INDEX IF NOT EXISTS bid_cards_status_idx ON bid_cards(status);
CREATE INDEX IF NOT EXISTS bid_cards_primary_category_idx ON bid_cards(primary_category);
CREATE INDEX IF NOT EXISTS bid_cards_primary_job_type_idx ON bid_cards(primary_job_type);

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_bid_cards_updated_at
BEFORE UPDATE ON bid_cards
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Row Level Security (RLS) policies for bid_cards table
ALTER TABLE bid_cards ENABLE ROW LEVEL SECURITY;

-- Policy: Homeowners can view bid cards associated with their projects.
-- (Assuming project ownership implies ability to see related bid cards)
CREATE POLICY bid_cards_homeowner_view_policy ON bid_cards
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM projects p
        WHERE p.id = bid_cards.project_id AND p.owner_id = auth.uid()
    ));

-- Policy: Service role can access all bid cards
CREATE POLICY bid_cards_service_policy ON bid_cards
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Note: More granular RLS for contractors (e.g., only seeing bid cards they are matched with or have bid on)
-- would be added later as the contractor interaction model is developed.
