CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT, password TEXT
);
CREATE TABLE IF NOT EXISTS messages(
    msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT, code TEXT, chat INTEGER, author INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS chat(
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author INTEGER, address INTEGER,
    encryption_enabled BOOLEAN DEFAULT 0,
    rotor_order TEXT DEFAULT '[1,2,3]',
    rotor_positions TEXT DEFAULT '["А","А","А"]',
    ring_settings TEXT DEFAULT '[0,0,0]',
    reflector TEXT DEFAULT 'B'
);