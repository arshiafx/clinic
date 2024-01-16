import sqlite3 as sql

conn = sql.connect(r'D:\AP\project\clinic\main.db')
cur = conn.cursor()

# Create table if it doesn't exist already
cur.execute('''CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            email TEXT, 
            password TEXT, 
            role TEXT,
            status INTEGER);
        ''')

cur.execute('DELETE FROM users;')    
users = [(10,'arshia','arshia@gmail.com','Salam0011','patient',0),(20,'parsa','parsa@gmail.com','strong','patient',0),(30,'arash','arash@','password','staff',0),(40,'mamad','@gmail.com','be to che','pashent',0),(50,'sadra','sadra@gmail.com','ramz','staff',0)]
cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);", users)
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
        conn.commit
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
                        role
                        status) 
                        VALUES(?,?,?,?,?);''',(user_id,full_name,email,password,role,0))
            conn.commit()
            print("user created successfully")
            return True

    def login(email,password):
        cur.execute('''SELECT password FROM users WHERE email = ?''', (email,))
        passwords = [row[0] for row in cur.fetchall()]
        if password in passwords:
            # Password matched, proceed with login
            cur.execute('''UPDATE users SET status = 1 WHERE email = ?''',(email,))
            conn.commit()
            print('login was succesful')
        else:
            # Password did not match
            print('Password did not match')

    def update(full_name,email,password,role):
        values=[]
        if full_name != "":values.append((5,"name",full_name))
        if email     != "":values.append((1,"email",email))
        if password  !="":values.append((2,"password",password))
        if role      !="" and role!=None:values.append((3,"role",role))
        if len(values)==0:return None
        query='''UPDATE users SET %s WHERE email=%s'''%(','.join(['%d=%s`']*len(values)),"'"+email+"'")
        cur.execute(query,tuple([i[2] for i in values]))
        conn.commit()
        return 'Profile updated Successfully!'
    
    def logout(email):
        cur.execute('''UPDATE users SET status = 0 WHERE email = ?''',(email,))
        conn.commit()
        print('User logged out')
        
    def get_info():
        user_data=cur.fetchone()
        data={}
        data['status']    = user_data[4]
        data['full_name'] = user_data[1]
        data['email']     = user_data[2]
        data['role']      = user_data[6]
        return data
    
    def view_appointmant():
        cur.execute("""select a.*,u.full_name from appointments as a
                    join users u on u.id=a.doctor_id where a.patient
                    =? order by date asc """,(users.get_info()["email"],))

class Notification:
    def init(self, notification_id, user_id, message, date_sent):

        self.notification_id = notification_id
        self.user_id = user_id
        self.message = message
        self.date_sent = date_sent

    @classmethod
    def send_notification(cls, user_id, message):
        date_sent = datetime.now()
        cur.execute('''INSERT INTO notification (user_id, message, date_sent)
                              VALUES (?, ?, ?)''', (user_id, message, date_sent))
        conn.commit()
        print("Notification sent successfully.")

class Review:
    def init(self, review_id, user_id, clinic_id, rating, comment, date_of_review):
        self.review_id = review_id
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.rating = rating
        self.comment = comment
        self.date_of_review = date_of_review

    @classmethod
    def submit_review(cls, user_id, clinic_id, rating, comment):

        current_datetime = datetime.now()
        cur.execute('''INSERT INTO review (user_id, clinic_id, rating, comment, date_of_review)
                    VALUES (?, ?, ?, ?, ?)''', (user_id, clinic_id, rating, comment, current_datetime))
        conn.commit()
        print("Review submitted successfully.")

    @classmethod
    def update_review(cls, review_id, new_rating, new_comment):
        cur.execute('''SELECT date_of_review FROM review WHERE review_id = ?''', (review_id,))
        review_date = cur.fetchone()

        if review_date and datetime.now() - datetime.strptime(review_date[0], "%Y-%m-%d %H:%M:%S") < timedelta(hours=3):
            cur.execute('''UPDATE review SET rating = ?, comment = ? WHERE review_id = ?''',
                        (new_rating, new_comment, review_id))
            conn.commit()
            print("Review updated successfully.")
        else:
            print("Review update not allowed after 3 hours of submission.")

    @classmethod
    def generate_average_ratings_table(cls):
        cur.execute('''SELECT clinic_id, AVG(rating) AS average_rating
                    FROM review
                    GROUP BY clinic_id''')
        result = cur.fetchall()

        if result:
            print("Clinic ID | Average Rating")
            print("----------------------------")
            for row in result:
                print(f"{row[0]}         | {row[1]:.2f}")
        else:
            print("No reviews available.")