import sqlite3
import hashlib
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 9999))

server.listen()

def log_sign_user(c):
    mode = c.recv(1024).decode()

    #log user in
    if mode == "1":
        print("logging in")
        
        usernameAndPassword = c.recv(1024).decode()
        username = usernameAndPassword.split(":")[0] #get username
        password = usernameAndPassword.split(":")[1] #get password
        
        password  = hashlib.sha256(password.encode()).hexdigest() #hash password

        print("RECEIVED")

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        #check for username and password in database
        cur.execute("SELECT * FROM userdata WHERE username = ? AND password = ?", (username, password))
        
        if cur.fetchall(): #username and password correct
            c.send("Success".encode()) #send success
            c.close()
        else: #username and password incorrect
            c.send("Fail".encode()) #send fail
            c.close()

    #sign user up
    elif mode == "2":
        print("signing up")

        usernameAndPassword = c.recv(1024).decode()
        username = usernameAndPassword.split(":")[0] #get username
        password = usernameAndPassword.split(":")[1] #get password
        
        password  = hashlib.sha256(password.encode()).hexdigest() #hash password

        print("RECEIVED")

        conn = sqlite3.connect("userdata.db")
        cur = conn.cursor()

        #insert new user into database
        cur.execute("INSERT INTO userdata (username, password, wins, draws, losses) VALUES (?, ?, ?, ?, ?)", (username, password, 0, 0, 0))
        conn.commit()

        c.send("Success".encode()) #send success
        c.close()

while True:
    client, addr = server.accept()
    log_sign_user(client)
