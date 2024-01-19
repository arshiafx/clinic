import sqlite3 as sql
import requests
import datetime
import secrets
import string


conn = sql.connect(r'D:\AP\project\clinic\main.db')
cur = conn.cursor()

# Create table if it doesn't exist already
cur.execute('''CREATE TABLE IF NOT EXISTS users(
            id integer PRIMARY KEY autoincrement, 
            name TEXT, 
            email TEXT, 
            password TEXT, 
            role TEXT,
            status INTEGER);
        ''')
cur.execute('''CREATE TABLE IF NOT EXISTS clinics(
            id integer PRIMARY KEY Autoincrement Not Null,
            name TEXT,
            address TEXT,
            phone_number TEXT,
            services TEXT,
            availability Integer not null);''' )

cur.execute('''CREATE TABLE IF NOT EXISTS queue(
            appointment_id integer PRIMARY KEY AUTOINCREMENT NOT NULL, 
            status VARCHAR(20) NOT NULL, 
            datetime text NOT NULL, 
            user_id INTEGER NOT NULL, 
            clinic_id INTEGER NOT NULL, 
            appointment_cost Integer);''')

cur.execute('''CREATE TABLE IF NOT EXISTS notification(
            notification_id integer PRIMARY KEY AUTOINCREMENT NOT NULL, 
            user_id INTEGER NOT NULL, 
            message TEXT NOT NULL, 
            date_sent VARCHAR(20) NOT NULL, 
            FOREIGN KEY(user_id) REFERENCES users(id))''')

cur.execute('''CREATE TABLE IF NOT EXISTS payment(
            payment_id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER NOT NULL,
            clinic_id INTEGER NOT NULL,
            appointment_id INTEGER NOT NULL,
            paid_amount REAL NOT NULL,
            payment_date VARCHAR(20) NOT NULL,
            payment_description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(clinic_id) REFERENCES clinic(id),
            FOREIGN KEY(appointment_id) REFERENCES queue(appointment_id))''')


cur.execute('DELETE FROM users;')  
user_data = [(None,'arshia','arshia@gmail.com','Salam0011','user',0),(None,'parsa','parsa@gmail.com','strong','user',0),(None,'arash','arash@','password','employee',0),(None,'mamad','@gmail.com','be to che','user',0),(None,'sadra','sadra@gmail.com','ramz','employee',0),(None,'aa','aa','aa','user',0)]
cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?);", user_data)
conn.commit()

cur.execute('DELETE FROM clinics;')  
clinics_data = [(None,'arshia','arshia@gmail.com','Salam0011','user',1),(None,'parsa','parsa@gmail.com','strong','user',1),(None,'arash','arash@','password','employee',1),(None,'mamad','@gmail.com','be to che','user',1),(None,'sadra','sadra@gmail.com','ramz','employee',1),(None,'aa','aa','aa','user',1)]
cur.executemany("INSERT INTO clinics VALUES(?, ?, ?, ?, ?, ?);", clinics_data)
conn.commit()

class users:
    global cur, status
    def __init__(self,user_id,full_name,email,password,role,status):
        self.user_id   = user_id
        self.full_name = full_name
        self.email     = email
        self.password  = password
        self.role      = role
        self.status      = status
        
    def sign_up(user_id,full_name,email,password,role,status):      
        cur.execute('''SELECT email FROM users;''')
        conn.commit
        emails = [email[0] for email in cur.fetchall()]
        if email in emails:
            print("user already exists")
            return False
        else:
            insert_text=('''INSERT INTO users(
                        id,
                        name,
                        email,
                        password,
                        role,
                        status) 
                        VALUES(?,?,?,?,?,?);''')
                        
            data =  (user_id,full_name,email,password,role,0)
            cur.execute(insert_text,data)            
            conn.commit()
            print("user created successfully")
            return True

    def login(email,password_type):
        global status, logged_in_user
        cur.execute('''SELECT password FROM users WHERE email = ?''', (email,))
        passwords = [row[0] for row in cur.fetchall()]
        if password_type == "password":
            password = input("please enter your password: ")
            if password in passwords:
                cur.execute('''UPDATE users SET status = 1 WHERE email = ?''',(email,))
                conn.commit()
                print('login was succesful')
                status = "1"
                logged_in_user = email
            else:
                print('Password or email are wrong.')        
        elif password_type.lower() == ["otp" or "One-Time Password"]:
            def generate_password():
                # Define the characters to use in the password
                characters = string.ascii_letters + string.digits

            # Generate a random seven-character password
                password = ''.join(secrets.choice(characters) for _ in range(7))

                return password

            otp = generate_password()
            print("Your One-Time Password:", otp)
            ask_otp = input("please enter your OTP: ")
            if otp == ask_otp:
                print('login was succesful')
                status = "1"
                logged_in_user = email
                del otp
            else:
                print("otp is wrong.")

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
        global status
        cur.execute('''UPDATE users SET status = 0 WHERE email = ?''',(email,))
        conn.commit()
        print('You have been logged out')
        status == "0"
    
    def get_info():
        user_data=cur.fetchone()
        data={}
        data['status']    = user_data[4]
        data['full_name'] = user_data[1]
        data['email']     = user_data[2]
        data['role']      = user_data[6]
        return data
    
    def view_appointmant():
        global status
        cur.execute("SELECT id FROM users WHERE email = ? ", (logged_in_user,))
        result = cur.fetchone()
        if status == "11":
            cur.execute("SELECT * FROM queue WHERE user_id = ? AND status = 'Booked' ", (result[0],))
            result = cur.fetchall()
            if result == []:
                print('There are no reserved appointments for you')
            else:
                for i in result:
                    print(i)
        elif status == "12":
            cur.execute("SELECT * FROM queue WHERE user_id = ? AND status = 'Finished' ", (result[0],))
            result = cur.fetchall()
            if result == []:
                print('You have not finished any of your appointments')
            else:
                for i in result:
                    print(i)

class clinic:
    def __init__(self,clinic_id,name,address,phone_number,services,availability):
        self.clinic_id    = clinic_id
        self.name         = name
        self.address      = address
        self.phone_num    = phone_number
        self.services     = services
        self.availability = availability
    
    def create_new_clinic(clinic_id,name,address,phone_number,services,availability):
        #check if clinic exists or not
        cur.execute('''SELECT phone_number FROM clinics;''')
        conn.commit
        phone_numbers = [phone_number[0] for phone_number in cur.fetchall()]
        if phone_number in phone_numbers:
            print("clinic already exists")
            return False

        else:
            cur.execute('''INSERT INTO clinics(
                        id,
                        name,
                        address,
                        phone_number,
                        services,
                        availability) 
                        VALUES(?,?,?,?,?,?);''',(clinic_id,name,address,phone_number,services,availability))
            conn.commit()
            print("clinic created successfully")
            return True  

    @classmethod
    def fetch_slots_data(cls):
        # Fetch data from the /slots endpoint of your app
        app_url = 'http://127.0.0.1:5000'  # Update this with the actual URL of your app
        response = requests.get(f'{app_url}/slots')
        
        if response.status_code == 200:
            slots_data = response.json()
            return slots_data
        else:
            print(f"Failed to fetch slots data. Status Code: {response.status_code}")
            return {}

    @classmethod
    def update_clinic_availability_from_api(cls):
        slots_data = cls.fetch_slots_data()

        for clinic_id, availability in slots_data.items():
            cur.execute('''Insert into clinics values(?,?,?,?,?,?)''', (clinic_id,None,None,None,None, availability))

        conn.commit()
        print("Clinic availability updated successfully from API.")

    @classmethod  
    def view_appointments(cls,clinic_id):
        global option
        cur.execute('''select appointment_id, user_id, datetime, appointment_cost from queue where clinic_id = ? and status = 'Boocked' ''', (clinic_id,))
        result = cur.fetchall()
        if result == []:
            print("The clinic doesn't have any booked appointments.")
            option = 0
        else:
            for row in result:
                appointment_id, user_id, datetime_str, appointment_cost = row

                cur.execute('select name from users where id = ?', (user_id,))
                result2 = cur.fetchone()

                if result2:
                    user_name = result2[0]            
                    print(f"Appointment: {appointment_id}  {user_name} {datetime_str} {appointment_cost}")
            option = 1

    @classmethod
    def set_availability(cls, clinic_id, new_availability):
        cur.execute('''UPDATE clinics SET availability = ? WHERE id = ?''', (new_availability, clinic_id))
        conn.commit()
        print("Availability updated successfully.")

    @classmethod
    def update_clinic_info(cls, clinic_id):
        
        cur.execute('''SELECT * FROM clinics WHERE id = ?''', (clinic_id,))
        existing_clinic = cur.fetchone()

        if existing_clinic:
            print("1. Update Name\n2. Update Address\n3. Update Phone Number\n4. Update Services")
            choice = input("Enter your choice (1/2/3/4): ")

            if choice == '1':
                new_name = input("Enter the new name: ")
                cur.execute('''UPDATE clinics SET name = ? WHERE id = ?''', (new_name, clinic_id))
            elif choice == '2':
                new_address = input("Enter the new address: ")
                cur.execute('''UPDATE clinics SET address = ? WHERE id = ?''', (new_address, clinic_id))
            elif choice == '3':
                new_phone_number = input("Enter the new phone number: ")
                cur.execute('''UPDATE clinics SET phone_number = ? WHERE id = ?''', (new_phone_number, clinic_id))
            elif choice == '4':
                new_services = input("Enter the new services (comma-separated): ")
                cur.execute('''UPDATE clinics SET services = ? WHERE id = ?''', (new_services, clinic_id))
            else:
                print("Invalid choice. clinics info update failed.")
                return

            conn.commit()
            print("Clinic info updated successful.")
        else:
            print("Clinic not found. Clinic info update failed.")
    
    @classmethod  
    def set_appointment_finished(cls, appointment_id):
        finished_status = 'Finished'
        cur.execute('''UPDATE queue SET status = ? 
                WHERE appointment_id = ?''', (finished_status, appointment_id))
        conn.commit()
        print("Appointment marked as finished successfully.")


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

class Queueing:
    def __init__(self, status, datetime, user_id, clinic_id, appointment_id, appointment_cost):
        self.status = status
        self.datetime = datetime
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.appointment_id = appointment_id
        self.appointment_cost = appointment_cost

    @classmethod
    def book_appointment(cls, user_id, clinic_id, appointment_cost):

        current_datetime = datetime.now()
        status = 'Booked'

        cur.execute('''INSERT INTO queue (status, datetime, user_id, clinic_id, appointment_cost) 
                    VALUES (?, ?, ?, ?, ?)''', (status, current_datetime, user_id, clinic_id, appointment_cost))
        conn.commit()
        print("Appointment booked successfully.")

    @classmethod
    def cancel_missed_appointments(cls, user_id):

        status = 'Booked'
        cur.execute('''UPDATE queue SET status = 'Cancelled' 
                    WHERE status = ? AND user_id = ? AND datetime < ?''', (status, user_id, datetime.now()))
        conn.commit()
        print("Missed appointments cancelled successfully.")

    @classmethod
    def reschedule_appointment(cls, user_id, clinic_id, new_datetime):

        status = 'Booked'
        cur.execute('''UPDATE queue SET datetime = ? 
                    WHERE status = ? AND user_id = ? AND clinic_id = ? AND datetime > ?''',
                           (new_datetime, status, user_id, clinic_id, datetime.now()))
        conn.commit()
        print("Appointment rescheduled successfully.")

class Payment:
    def __init__(self, payment_id, user_id, clinic_id, appointment_id,
    paid_amount, payment_date, payment_description):
        self.payment_id = payment_id
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.appointment_id = appointment_id
        self.paid_amount = paid_amount
        self.payment_date = payment_date
        self.payment_description = payment_description

    @classmethod
    def process_payment(cls, user_id, clinic_id, payment_description):

        cur.execute('''SELECT appointment_id, status, appointment_cost FROM
        queue
        WHERE user_id = ? AND clinic_id = ? AND status IN
        ('Booked', 'Rescheduled')
        ORDER BY datetime DESC LIMIT 1''', (user_id, clinic_id))
        appointment_details = cur.fetchone()

        if appointment_details:
            appointment_id, status, appointment_cost = appointment_details
            paid_amount = appointment_cost if status == 'Booked' else 0.0
            payment_date = datetime.now()
            conn.execute('''INSERT INTO payment (user_id, clinic_id,
            appointment_id, paid_amount, payment_date, payment_description)
            VALUES (?, ?, ?, ?, ?, ?)''', (user_id, clinic_id,
            appointment_id, paid_amount, payment_date, payment_description))
            conn.commit()
            print("Payment processed successfully.")
        else:
            print("No eligible appointment found for payment.")

