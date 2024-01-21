import secrets
import string
import sqlite3 as sql

conn = sql.connect(r'database.db')
cur = conn.cursor()

class users:
    global cur
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
    #def get_info():
        #user_data=cur.fetchone()
        #data={}
        #data['status']    = user_data[4]
        #data['full_name'] = user_data[1]
        #data['email']     = user_data[2]
        #data['role']      = user_data[6]
        #return data
    
    def view_appointmant():
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

class Queueing:
    def __init__(self, status, datetime, user_id, clinic_id, appointment_id, appointment_cost):
        self.status = status
        self.datetime = datetime
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.appointment_id = appointment_id
        self.appointment_cost = appointment_cost

    @classmethod
    def book_appointment(cls,user_id, clinic_id):

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Appointment_status = 'Booked'

        cur.execute('''INSERT INTO queue VALUES (?, ?, ?, ?, ?, ?)''', (None, Appointment_status, current_datetime, user_id, int(clinic_id), None))
        conn.commit()
        cur.execute('''select availability from clinics where clinic_id = ?''',(int(clinic_id),))
        result = cur.fetchall()
        new_availability = result[0] - 1
        cur.execute('''UPDATE clinics SET availability = ? 
                    where clinic_id = ?''',(new_availability, int(clinic_id)))
        conn.commit()
        print("Appointment booked successfully.")
    @classmethod
    def cancelled_appointment(cls,clinic_id):
        Appointment_status = 'Booked'
        if int(clinic_id) in clinic_ids:
            cur.execute('''UPDATE queue SET status = 'Cancelled' 
                        where appointment_id = ? and status = ?''',(int(clinic_id), Appointment_status))
            conn.commit()
            print('The appointment has been cancelled')
        else:
            print('Wrong input')

    @classmethod
    def missed_appointments(cls, user_id):

        Appointment_status = 'Booked'
        cur.execute('''UPDATE queue SET status = 'Missed' 
                    WHERE status = ? AND user_id = ? AND datetime != ?''', 
                    (Appointment_status, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        print("Missed appointments cancelled successfully.")

    @classmethod
    def reschedule_appointment(cls, user_id, clinic_id):
        new_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute('''UPDATE queue SET datetime = ? 
                    WHERE status = ? AND user_id = ? AND clinic_id = ? AND datetime > ?''',
                           (new_datetime, status, user_id, clinic_id, datetime.now()))
        conn.commit()
        print("Appointment rescheduled successfully.")


class Patient(users):

    def option_one():  # current reservations
        global status, cursor
        status = "11"
        users.view_appointmant()
        # get from database

    def option_two():  # show history
        global status, cursor
        # get history from database
        status = "12"
        users.view_appointmant()

    def option_three():  # new reservation
        global status, cursor
        cur.execute("SELECT id FROM users WHERE email = ? ", (logged_in_user,))
        temp_user_id = cur.fetchone()
        status = "13"
        search_key = input("search: ")
        search_key = f"{search_key}"
        cur.execute("SELECT id , name FROM clinics WHERE name = ? AND availability != 0 ", (search_key,))
        result = cur.fetchall()
        if result == []:
            print('There are no available appointments for any clinics')
        else:
            for i in result:
                print(f"Clinic: {i[0]} {i[1]}")

        input_id = input("enter the number of the clinic you want to make an appointment for:")
        clinic_ids = [clinic[0] for clinic in result]
        if int(input_id) in clinic_ids:
            cur.execute('''select id from clinics where id = ?''',(int(input_id),))
            temp_clinic_id = cur.fetchone()
            Queueing.book_appointment(int(temp_user_id[0]),int(temp_clinic_id[0]))
        else:
            print('Wrong input')

