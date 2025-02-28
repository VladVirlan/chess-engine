import sqlite3
import hashlib

#create database
conn = sqlite3.connect("userdata.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS userdata (
    id INTEGER PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    wins INTEGER NOT NULL,
    draws INTEGER NOT NULL,
    losses INTEGER NOT NULL
)
""")

#insert into database
username1, password1 = "VLADIMUS", hashlib.sha256("12345678".encode()).hexdigest()

cur.execute("INSERT INTO userdata (username, password, wins, draws, losses) VALUES (?, ?, ?, ?, ?)", (username1, password1, 0, 0, 0))
conn.commit()
