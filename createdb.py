import sqlite3

conn = sqlite3.connect("standupbot.db")
cursor = conn.cursor()

# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON")

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE groups (
    id TEXT PRIMARY KEY,
    group_name TEXT NOT NULL,
    server_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (group_name, server_id)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS group_members (
    user_id TEXT NOT NULL,
    group_id TEXT NOT NULL,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS team_leaders (
    group_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    group_id TEXT NOT NULL, 
    task_name TEXT NOT NULL,
    task_description TEXT,
    is_completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    group_id TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id)
)
''')

cursor.executemany('''
    INSERT INTO questions (question_text)
    VALUES (?);
''', [
    ('What have you worked on in the past week?',),
    ('How many hours have you worked in the past week?',),
    ('Are there any blockers or challenges?',)
])

#example mock data

# cursor.executemany('''
#     INSERT INTO users (id, username)
#     VALUES (?,?);
# ''', [
#     ('user1','cool username'),
#     ('user2','bad username')
# ])

# cursor.executemany('''
#     INSERT INTO groups (group_name, server_id)
#     VALUES (?, ?);
# ''', [
#     ('group1','server1'),
#     ('group2','server1'),
#     ('group3','server2'),
# ])

# cursor.executemany('''
#     INSERT INTO group_members (group_id, user_id)
#     VALUES (?, ?);
# ''', [
#     (1, 'user1'),
#     (1, 'user2'),
#     (1, 'user3'),
#     (2, 'user1'),
# ])

# cursor.executemany('''
#     INSERT INTO responses (response_text, user_id, group_id, question_id)
#     VALUES (?,?,?,?);
# ''', [
#     ('i worked on nothing','user1',1,1),
#     ('i worked 18 hours','user1',1,2),
#     ('i had no challenges','user1',1,3),
#     ('i worked on nothing','user2',1,1),
#     ('i worked on nothing','user2',2,1)
# ])


# cursor.execute('''
#     SELECT u.username, r.response_text
#     FROM responses r 
#     JOIN users u ON u.id = r.user_id
#     JOIN groups g ON g.id = r.group_id
#     WHERE u.username = 'cool username'
#     AND g.group_name = 'group1';
# ''')

# rows = cursor.fetchall()
# for row in rows:
#     print(row)

conn.commit()
conn.close()

