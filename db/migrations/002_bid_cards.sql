-- Create bid_cards table for InstaBids MVP
-- This migration adds the bid_cards table and associated indexes

-- Create bid_cards table
CREATE TABLE IF NOT EXISTS bid_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    job_type TEXT NOT NULL,
    budget_range TEXT,
    timeline TEXT,
    group_bidding BOOLEAN DEFAULT false,
    scope_json JSONB,
    photo_meta JSONB,
    ai_confidence FLOAT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'final')),
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    CONSTRAINT bid_cards_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects(id) ON DELETE CASCADE
);

COMMENT ON TABLE bid_cards IS 'Bid cards generated for projects to send to contractors';
COMMENT ON COLUMN bid_cards.id IS 'Unique identifier for the bid card';
COMMENT ON COLUMN bid_cards.project_id IS 'Reference to the associated project';
COMMENT ON COLUMN bid_cards.category IS 'Primary category of the project (repair, renovation, etc.)';
COMMENT ON COLUMN bid_cards.job_type IS 'Specific job type within the category';
COMMENT ON COLUMN bid_cards.budget_range IS 'Expected budget range for the project';
COMMENT ON COLUMN bid_cards.timeline IS 'Expected timeline for project completion';
COMMENT ON COLUMN bid_cards.group_bidding IS 'Whether multiple contractors can collaborate on this project';
COMMENT ON COLUMN bid_cards.scope_json IS 'Detailed scope information in JSON format';
COMMENT ON COLUMN bid_cards.photo_meta IS 'Metadata and analysis of uploaded project photos';
COMMENT ON COLUMN bid_cards.ai_confidence IS 'AI confidence score for the classification (0.0-1.0)';
COMMENT ON COLUMN bid_cards.status IS 'Status of the bid card (draft or final)';

-- Create indexes for bid_cards
CREATE INDEX IF NOT EXISTS bid_cards_project_id_idx ON bid_cards(project_id);
CREATE INDEX IF NOT EXISTS bid_cards_category_idx ON bid_cards(category);
CREATE INDEX IF NOT EXISTS bid_cards_job_type_idx ON bid_cards(job_type);
CREATE INDEX IF NOT EXISTS bid_cards_status_idx ON bid_cards(status);

-- Enable RLS for bid_cards table
ALTER TABLE bid_cards ENABLE ROW LEVEL SECURITY;

-- Policy: Homeowners can only view bid cards for their own projects
CREATE POLICY bid_cards_owner_policy ON bid_cards
    USING (EXISTS (
        SELECT 1 FROM projects 
        WHERE projects.id = bid_cards.project_id 
        AND projects.owner_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects 
        WHERE projects.id = bid_cards.project_id 
        AND projects.owner_id = auth.uid()
    ));

-- Policy: Service role can access all bid cards
CREATE POLICY bid_cards_service_policy ON bid_cards
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for bid_cards
CREATE TRIGGER set_bid_cards_updated_at
BEFORE UPDATE ON bid_cards
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create function to update project status when bid card is created/updated
CREATE OR REPLACE FUNCTION update_project_status_on_bid_card_change()
RETURNS TRIGGER AS $$
BEGIN
    -- If the bid card status is 'final', update the project status to 'bid_ready'
    IF NEW.status = 'final' THEN
        UPDATE projects
        SET status = 'bid_ready'
        WHERE id = NEW.project_id
        AND status IN ('draft', 'scoping');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for bid_cards
CREATE TRIGGER update_project_status_on_bid_card
AFTER INSERT OR UPDATE OF status ON bid_cards
FOR EACH ROW
EXECUTE FUNCTION update_project_status_on_bid_card_change();