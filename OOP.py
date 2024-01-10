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
        emails = cur.execute('''SELECT email FROM users;''')
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
    
