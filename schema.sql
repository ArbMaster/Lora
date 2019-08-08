CREATE TABLE IF NOT EXISTS Payload (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deveui TEXT NOT NULL,
    payload TEXT NOT NULL,
    ts REAL NOT NULL,
    FOREIGN KEY(deveui) REFERENCES Device(deveui)
);

CREATE TABLE IF NOT EXISTS Profile (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    decoder TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Device (
    deveui TEXT PRIMARY KEY,
    pid INTEGER NOT NULL,
    FOREIGN KEY(pid) REFERENCES Profile(pid)
)WITHOUT ROWID;

CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

--TODO: Add indices based on performance requirement
CREATE TABLE IF NOT EXISTS UserDevice (
    uid INTEGER NOT NULL,
    deveui TEXT NOT NULL,
    FOREIGN KEY (uid) REFERENCES User(id),
    FOREIGN KEY (deveui) REFERENCES Device(deveui)
);

CREATE TABLE IF NOT EXISTS Session (
    cookie TEXT NOT NULL PRIMARY KEY,
    uid INTEGER NOT NULL,
    ts TIMESTAMP DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (uid) REFERENCES User(id)
)WITHOUT ROWID;