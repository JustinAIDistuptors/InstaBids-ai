-- Add messages and user_preferences tables for InstaBids MVP
-- This migration adds tables for messaging and user preferences

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('homeowner', 'contractor', 'agent')),
    content TEXT NOT NULL,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    CONSTRAINT messages_project_id_fkey FOREIGN KEY (project_id)
        REFERENCES projects(id) ON DELETE CASCADE
);

COMMENT ON TABLE messages IS 'Messages exchanged between homeowners, contractors, and agents';
COMMENT ON COLUMN messages.id IS 'Unique identifier for the message';
COMMENT ON COLUMN messages.project_id IS 'Reference to the associated project';
COMMENT ON COLUMN messages.sender IS 'Role of the message sender (homeowner, contractor, or agent)';
COMMENT ON COLUMN messages.content IS 'Content of the message';
COMMENT ON COLUMN messages.inserted_at IS 'Timestamp when the message was sent';

-- Create indexes for messages
CREATE INDEX IF NOT EXISTS messages_project_id_idx ON messages(project_id);
CREATE INDEX IF NOT EXISTS messages_sender_idx ON messages(sender);
CREATE INDEX IF NOT EXISTS messages_inserted_at_idx ON messages(inserted_at);

-- Enable RLS for messages table
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Policy: Homeowners can only view and create messages for their own projects
CREATE POLICY messages_owner_policy ON messages
    USING (EXISTS (
        SELECT 1 FROM projects 
        WHERE projects.id = messages.project_id 
        AND projects.owner_id = auth.uid()
    ))
    WITH CHECK (EXISTS (
        SELECT 1 FROM projects 
        WHERE projects.id = messages.project_id 
        AND projects.owner_id = auth.uid()
    ) AND sender = 'homeowner');

-- Policy: Service role can access all messages
CREATE POLICY messages_service_policy ON messages
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 0.5,
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES auth.users(id) ON DELETE CASCADE,
    CONSTRAINT user_preferences_unique_key UNIQUE (user_id, preference_key)
);

COMMENT ON TABLE user_preferences IS 'Stored user preferences for homeowners';
COMMENT ON COLUMN user_preferences.id IS 'Unique identifier for the preference';
COMMENT ON COLUMN user_preferences.user_id IS 'Reference to the user';
COMMENT ON COLUMN user_preferences.preference_key IS 'Key identifying the preference type';
COMMENT ON COLUMN user_preferences.preference_value IS 'Value of the preference';
COMMENT ON COLUMN user_preferences.confidence IS 'Confidence score (0.0-1.0) for AI-derived preferences';

-- Create indexes for user_preferences
CREATE INDEX IF NOT EXISTS user_preferences_user_id_idx ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS user_preferences_key_idx ON user_preferences(preference_key);

-- Enable RLS for user_preferences table
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own preferences
CREATE POLICY user_preferences_owner_policy ON user_preferences
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- Policy: Service role can access all preferences
CREATE POLICY user_preferences_service_policy ON user_preferences
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Create trigger for user_preferences
-- Assumes update_updated_at_column() function is created by 002_bid_cards.sql or similar
CREATE TRIGGER set_user_preferences_updated_at
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();