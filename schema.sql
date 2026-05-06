CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    started_at TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    action_taken TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    FOREIGN KEY (user_id) REFERENCES users(id)
);