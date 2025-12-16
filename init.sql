CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL, 
    username VARCHAR(255) UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_users_id ON users(id);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    CONSTRAINT unique_category_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_categories_id ON categories(id);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    description TEXT,
    content_type VARCHAR(50) NOT NULL, 
    release_year INTEGER,
    imdb_rating DOUBLE PRECISION,
    imdb_id VARCHAR(20) UNIQUE,
    poster_url VARCHAR(500),
    genre VARCHAR(255),
    director VARCHAR(255),
    actors_cast TEXT,
    language VARCHAR(100),
    country VARCHAR(100),

    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_content_id ON content(id);
CREATE INDEX IF NOT EXISTS idx_content_title ON content(title);
CREATE INDEX IF NOT EXISTS idx_content_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_release_year ON content(release_year);
CREATE INDEX IF NOT EXISTS idx_content_imdb_rating ON content(imdb_rating);
CREATE INDEX IF NOT EXISTS idx_content_category_id ON content(category_id);
CREATE INDEX IF NOT EXISTS idx_content_is_active ON content(is_active);

ALTER TABLE content ADD CONSTRAINT check_content_type 
    CHECK (content_type IN ('movie', 'series'));


CREATE TABLE IF NOT EXISTS view_history (
    id SERIAL PRIMARY KEY,
    
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    watched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    rating DOUBLE PRECISION CHECK (rating >= 1 AND rating <= 10),
    rewatch BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);


CREATE INDEX IF NOT EXISTS idx_view_history_id ON view_history(id);
CREATE INDEX IF NOT EXISTS idx_view_history_user_id ON view_history(user_id);
CREATE INDEX IF NOT EXISTS idx_view_history_content_id ON view_history(content_id);
CREATE INDEX IF NOT EXISTS idx_view_history_watched_at ON view_history(watched_at);
CREATE INDEX IF NOT EXISTS idx_view_history_user_content ON view_history(user_id, content_id);

ALTER TABLE view_history ADD CONSTRAINT unique_view_record 
    UNIQUE (user_id, content_id, watched_at);

CREATE TABLE IF NOT EXISTS watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_watchlist_id ON watchlist(id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_content_id ON watchlist(content_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_user_content ON watchlist(user_id, content_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_priority ON watchlist(priority);
CREATE INDEX IF NOT EXISTS idx_watchlist_added_at ON watchlist(added_at);


ALTER TABLE watchlist ADD CONSTRAINT unique_watchlist_item 
    UNIQUE (user_id, content_id);


DO $$
BEGIN
    RAISE NOTICE 'База данных успешно инициализирована';
    RAISE NOTICE 'Создано таблиц: 5 (users, categories, content, view_history, watchlist)';
END $$;
