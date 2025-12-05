-- Base schema for storing Telegram news posts in Postgres
-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Channels we monitor in Telegram
CREATE TABLE IF NOT EXISTS telegram_channels (
    id              BIGSERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        TEXT,
    title           TEXT,
    description     TEXT,
    language_code   TEXT,
    is_monitored    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Raw posts fetched from Telegram (idempotent by channel + message id)
CREATE TABLE IF NOT EXISTS raw_posts (
    id                  BIGSERIAL PRIMARY KEY,
    channel_id          BIGINT NOT NULL REFERENCES telegram_channels(id) ON DELETE CASCADE,
    source_message_id   BIGINT NOT NULL,
    posted_at           TIMESTAMPTZ NOT NULL,
    fetched_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    edit_date           TIMESTAMPTZ,
    text                TEXT,
    media               JSONB,
    link_preview        JSONB,
    language_code       TEXT,
    checksum            BYTEA,
    UNIQUE(channel_id, source_message_id)
);
CREATE INDEX IF NOT EXISTS raw_posts_channel_idx ON raw_posts(channel_id, posted_at DESC);

-- Media files attached to a post (photo/video/document)
CREATE TABLE IF NOT EXISTS media_assets (
    id              BIGSERIAL PRIMARY KEY,
    raw_post_id     BIGINT NOT NULL REFERENCES raw_posts(id) ON DELETE CASCADE,
    media_type      TEXT NOT NULL CHECK (media_type IN ('photo','video','document','audio','voice','animation','other')),
    file_id         TEXT NOT NULL,
    file_unique_id  TEXT,
    mime_type       TEXT,
    file_size       INTEGER,
    width           INTEGER,
    height          INTEGER,
    duration_sec    INTEGER,
    caption         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS media_assets_post_idx ON media_assets(raw_post_id);

-- Structured links extracted from posts (t.me links, external URLs)
CREATE TABLE IF NOT EXISTS post_links (
    id              BIGSERIAL PRIMARY KEY,
    raw_post_id     BIGINT NOT NULL REFERENCES raw_posts(id) ON DELETE CASCADE,
    url             TEXT NOT NULL,
    url_type        TEXT CHECK (url_type IN ('telegram','external','unknown')),
    domain          TEXT,
    text            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS post_links_post_idx ON post_links(raw_post_id);

-- LLM annotations for posts
CREATE TABLE IF NOT EXISTS enriched_posts (
    id              BIGSERIAL PRIMARY KEY,
    raw_post_id     BIGINT NOT NULL UNIQUE REFERENCES raw_posts(id) ON DELETE CASCADE,
    status          TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','processing','ready','error')),
    title           TEXT,
    summary         TEXT,
    tags            TEXT[],
    sentiment       TEXT,
    embedding       VECTOR(1536),
    llm_model       TEXT,
    embedding_model TEXT,
    processed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS enriched_posts_status_idx ON enriched_posts(status);
CREATE INDEX IF NOT EXISTS enriched_posts_embedding_idx ON enriched_posts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Simple deduplication candidates by checksum across channels
CREATE TABLE IF NOT EXISTS duplicate_candidates (
    checksum        BYTEA NOT NULL,
    raw_post_id     BIGINT NOT NULL REFERENCES raw_posts(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (checksum, raw_post_id)
);

-- Lightweight queue for background workers
CREATE TABLE IF NOT EXISTS processing_queue (
    id              BIGSERIAL PRIMARY KEY,
    raw_post_id     BIGINT NOT NULL REFERENCES raw_posts(id) ON DELETE CASCADE,
    task_type       TEXT NOT NULL CHECK (task_type IN ('annotate','embed','cluster')),
    priority        SMALLINT NOT NULL DEFAULT 5,
    available_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    attempts        SMALLINT NOT NULL DEFAULT 0,
    last_error      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS processing_queue_available_idx ON processing_queue(task_type, priority, available_at);

-- Trigger to keep updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER channels_updated_at BEFORE UPDATE ON telegram_channels
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

CREATE TRIGGER raw_posts_updated_at BEFORE UPDATE ON raw_posts
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

CREATE TRIGGER enriched_posts_updated_at BEFORE UPDATE ON enriched_posts
FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

