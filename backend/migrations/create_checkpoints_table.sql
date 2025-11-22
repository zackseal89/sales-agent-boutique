-- Create checkpoints table for LangGraph conversation memory
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/gqzqpjsxvfqcbxjjxfzb/sql

CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- Create index for faster lookups by thread_id
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread_id ON checkpoints(thread_id);

-- Add comment
COMMENT ON TABLE checkpoints IS 'Stores LangGraph conversation state for persistent memory across sessions';

-- Create checkpoints_writes table for LangGraph (required for AsyncPostgresSaver)
CREATE TABLE IF NOT EXISTS checkpoints_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

COMMENT ON TABLE checkpoints_writes IS 'Stores pending writes for LangGraph checkpoints';
