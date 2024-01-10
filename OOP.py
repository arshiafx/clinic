import sqlite3 as sql

conn = sql.connect(r'D:\AP\project\clinic\main.db')
cur = conn.cursor()
# Create table if it doesn't exist already
cur.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            email TEXT, 
            password TEXT, 
            role TEXT);
        ''')

cur.execute('DELETE FROM users;')    
users = [(10,'arshia','arshia@gmail.com','Salam0011','patient'),(20,'parsa','parsa@gmail.com','strong','patient'),(30,'arash','arash@','password','staff'),(40,'mamad','@gmail.com','be to che','pashent'),(50,'sadra','sadra@gmail.com','ramz','staff')]
cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?);", users)
conn.commit()

class users:
    global cur
    
    def __init__(self,user_id,full_name,email,password,role):
        self.user_id   = user_id
        self.full_name = full_name
        self.email     = email
        self.password  = password
        self.role      = role
        
    def sign_up(user_id,full_name,email,password,role):      
        #check if user exists or not
        cur.execute('''SELECT email FROM users;''')
        emails = [email[0] for email in cur.fetchall()]
        if email in emails:
            print("user already exists")
            return False
        
        #if user doesn't exist we sign them up
        else:
            cur.execute('''INSERT INTO users(
                        id,
                        name,
                        email,
                        password,
                        role) 
                        VALUES(?,?,?,?,?);''',(user_id,full_name,email,password,role))
            conn.commit()
            print("user created successfully")
            return True

    def login():
        pass