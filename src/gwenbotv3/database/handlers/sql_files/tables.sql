CREATE TABLE IF NOT EXISTS Users(
    user_id INTEGER PRIMARY KEY,
    user_name TEXT,
    is_anonymised BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Servers(
    server_id INTEGER PRIMARY KEY,
    owner_id INTEGER,
    member_count INTEGER,
    quote BOOLEAN
);

CREATE TABLE IF NOT EXISTS Gwenseek(
    g_id INTEGER PRIMARY KEY,
    user INTEGER,
    server INTEGER
    user_message TEXT,
    reasoning_content TEXT,
    FOREIGN KEY (user) REFERENCES Users(user_id)
    FOREIGN KEY (server) REFERENCES Servers(server_id)
);

CREATE TABLE IF NOT EXISTS QuestionCount(
    q_id INTEGER PRIMARY KEY,
    amount INTEGER,
    latest_user INTEGER,
    server INTEGER UNIQUE,
    channel_id INTEGER UNIQUE,
    symbol TEXT,
    creating_user INTEGER,
    FOREIGN KEY (latest_user) REFERENCES Users(user_id),
    FOREIGN KEY (creating_user) REFERENCES Users(user_id),
    FOREIGN KEY (server) REFERENCES Servers(server_id),
);

CREATE TABLE IF NOT EXISTS QuestionUser(
    q_user_id INTEGER PRIMARY KEY,
    user INTEGER,
    questions_server INTEGER,
    amount INTEGER,
    FOREIGN KEY (user) REFERENCES Users(user_id),
    FOREIGN KEY (questions_server) REFERENCES Servers(server_id),
    UNIQUE (user, questions_server)
);

CREATE TABLE IF NOT EXISTS Subs(
    sub_id INTEGER PRIMARY KEY,
    user INTEGER,
    server INTEGER,
    FOREIGN KEY (user) REFERENCES Users(user_id),
    FOREIGN KEY (server) REFERENCES Servers(server_id),
    UNIQUE (user, server)
);

CREATE TABLE IF NOT EXISTS Blacklist(
    blacklist_id INTEGER PRIMARY KEY,
    user INTEGER,
    server INTEGER,
    by_owner BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user) REFERENCES Users(user_id),
    FOREIGN KEY (server) REFERENCES Servers(server_id)
    UNIQUE (user, server, by_owner)
);