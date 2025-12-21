CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL, 
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);


CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    description TEXT,
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('movie', 'series')), 
    release_year INTEGER,
    imdb_rating DOUBLE PRECISION,
    imdb_id VARCHAR(20) UNIQUE,
    poster_url VARCHAR(500),
    genre VARCHAR(255),
    director VARCHAR(255),
    actors_cast TEXT,
    language VARCHAR(100),
    country VARCHAR(100),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_content_content_type ON content(content_type);


CREATE TABLE IF NOT EXISTS view_history (
    id SERIAL PRIMARY KEY,
    
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    watched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rating DOUBLE PRECISION CHECK (rating >= 1 AND rating <= 10),
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, content_id, watched_at)
);

CREATE INDEX IF NOT EXISTS idx_view_history_user_id ON view_history(user_id);
CREATE INDEX IF NOT EXISTS idx_view_history_watched_at ON view_history(watched_at);
CREATE INDEX IF NOT EXISTS idx_view_history_user_content ON view_history(user_id, content_id);

CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    CONSTRAINT unique_watchlist_item UNIQUE (user_id, content_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_content ON watchlist(user_id, content_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_added_at ON watchlist(added_at);

DO $$
BEGIN
    RAISE NOTICE 'База данных успешно инициализирована';
    RAISE NOTICE 'Создано таблиц: 4 (users, content, view_history, watchlist)';
END $$;
