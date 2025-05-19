-- Initialize database schema for InstaBids MVP
-- This migration creates the initial tables and security policies

-- Enable the pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES auth.users(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    zipcode TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'scoping', 'bid_ready', 'matched')),
    inserted_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    
    CONSTRAINT projects_owner_id_fkey FOREIGN KEY (owner_id)
        REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE projects IS 'Home improvement projects created by homeowners';
COMMENT ON COLUMN projects.id IS 'Unique identifier for the project';
COMMENT ON COLUMN projects.owner_id IS 'Reference to the homeowner (auth.users)';
COMMENT ON COLUMN projects.title IS 'Brief title of the project';
COMMENT ON COLUMN projects.description IS 'Detailed description of the project';
COMMENT ON COLUMN projects.zipcode IS 'Location zipcode for the project';
COMMENT ON COLUMN projects.status IS 'Current status of the project workflow';
COMMENT ON COLUMN projects.inserted_at IS 'Timestamp when the project was created';

-- Create indexes
CREATE INDEX IF NOT EXISTS projects_owner_id_idx ON projects(owner_id);
CREATE INDEX IF NOT EXISTS projects_status_idx ON projects(status);
CREATE INDEX IF NOT EXISTS projects_zipcode_idx ON projects(zipcode);

-- Row Level Security (RLS) policy for projects table
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Policy: Homeowners can only view and update their own projects
CREATE POLICY projects_owner_policy ON projects
    USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

-- Policy: Service role can access all projects
CREATE POLICY projects_service_policy ON projects
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Create base schema for user profiles (to be extended later)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    full_name TEXT,
    avatar_url TEXT,
    user_type TEXT NOT NULL CHECK (user_type IN ('homeowner', 'contractor', 'property_manager')),
    
    CONSTRAINT profiles_id_fkey FOREIGN KEY (id)
        REFERENCES auth.users(id) ON DELETE CASCADE
);

COMMENT ON TABLE profiles IS 'Extended profile information for users';
COMMENT ON COLUMN profiles.user_type IS 'Type of user (homeowner, contractor, property_manager)';

-- Row Level Security for profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view and update their own profiles
CREATE POLICY profiles_owner_policy ON profiles
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- Policy: Service role can access all profiles
CREATE POLICY profiles_service_policy ON profiles
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');