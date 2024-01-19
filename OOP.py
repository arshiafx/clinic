import sqlite3 as sql
import requests
import datetime

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
          
    #def update(name,address,phone_number,services,availability):
        #pass

#    def view_appointmant():
#        """
 #       This function is used to display all the appointments of a particular clinic.
#        It takes one argument i.e., clinic_id and returns None.
#        """
#        def view_appointments_by_clinic(clinic_id):
#            cur.execute('''SELECT a.*, u.full_name 
 #                          FROM appointments AS a
 #                          JOIN users AS u ON u.id = a.doctor_id 
 #                          WHERE a.clinic_id = ? 
#                           ORDER BY a.date ASC''', (clinic_id,))
 #           appointments = cur.fetchall()
  #          for appointment in appointments:
#                print(appointment)
 #               # If no arguments are passed then it will show all the appointments from all the clinic
#        def view_appointments():
 #           cur.execute('''SELECT a.*, u.full_name 
 #                           FROM appointments AS a
 #                           JOIN users AS u ON u.id = a.doctor_id 
 #                           ORDER BY a.date ASC''')
 #           appointments = cur.fetchall()
 #           for appointment in appointments:
#                print(appointment)
                        
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
            cur.execute('''UPDATE clinics SET availability = ? WHERE id = ?''', (availability, clinic_id))

        conn.commit()
        print("Clinic availability updated successfully from API.")
##############################

    @classmethod
    def view_appointments(cls, clinic_id):
        
        cur.execute('''SELECT * FROM queue WHERE clinic_id = ? AND status = 'Booked' ORDER BY datetime''', (clinic_id,))
        appointments = cur.fetchall()

        if appointments:
            print("Clinic's booked appointments:")
            for appointment in appointments:
                appointment_id, status, datetime_str, user_id, _, appointment_cost = appointment
                print(f"Appointment ID: {appointment_id}, Status: {status}, DateTime: {datetime_str}, User ID: {user_id}, Cost: {appointment_cost}")
        else:
            print("The clinic doesn't have any booked appointments.")

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
            print("Clinic info update successful.")
        else:
            print("Clinic not found. Clinic info update failed.")


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

