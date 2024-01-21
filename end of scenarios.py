import secrets
import string
import sqlite3 as sql
import requests
from datetime import datetime

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
##############################

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


class Employee(users):
    def option_one():  # current reservations
        global status
        status = "11"
        if int(input_id) in clinic_ids:
            clinic.view_appointments(int(input_id))
        else:
            print('Wrong input')
    def option_two():  # cancel reservations
        global status, option
        if int(input_id) in clinic_ids:
            clinic.view_appointments(int(input_id))
            if option == 1:
                input_ap_id = input('Enter the number of the appointment you want to cancel:')
                Queueing.cancelled_appointment(int(input_ap_id))
            else:
                pass
        else:
            print('Wrong input')
       

    def option_three():  # increase availability
        global status
        status = "13"
        number_of_new_slots = int(input("how many appointment slots do you want to add to the clinic?: "))
        cur.execute('select availability from clinics where clinic_id = ?',(int(input_id),))
        clinic_availability = cur.fetchone()
        new_availability = clinic_availability[0] + number_of_new_slots
        clinic.set_availability(input_id, new_availability)
        
status = "0"
logged_in_user = str()
print("Welcome!")
def handle_backing_option():
    global status
    backing = input('Please choose one option:\n1. Back\n2. Log Out\n')
    if backing == "1":
        status = "1"
    elif backing == "2":
        users.logout(logged_in_user)
    else:
        print('Wrong input')

while True:

    if status == "0":
        order = input("Please sign up or login\n")
        if order.lower() in ["sign up", "signup"]:
            info = {
                "Full name": "",
                "email address": "",
                "role(user/employee)": "",
                "password": ""
            }
            for i in info:
                info[f'{i}'] = input(f"please enter your {i}: ")
            users.sign_up(None, info["Full name"], info["email"], info["password"], info["role(patient/staff)"], 0)
        elif order.lower() in ["login"]:
            email = input("please enter your email: ")
            password_type = input("password or One-Time Password(otp): ")
            users.login(email, password_type)

    elif status == "1":
        cur.execute("SELECT role FROM users WHERE email = ? ", (logged_in_user,))
        Role = cur.fetchone()
        Role = str(Role[0])
        if Role.lower() in ["user"]:
            order = input('1.Reserved Appointments \n2.Appointment History \n3.Make an Appointmnet\n4.Log Out \nPlease choose one option:' )
            if order == "1":
                Patient.option_one()
                handle_backing_option()
            elif order == "2":
                Patient.option_two()
                handle_backing_option()
            elif order == "3":
                Patient.option_three()
                handle_backing_option()
            elif order == "4":
                users.logout(email)
                status = "0"
            else:
                print('Wrong input')
        elif Role.lower() in ["employee"]:
            cur.execute("SELECT id , name FROM clinics")
            result = cur.fetchall()
            for i in result:
                print(f"Clinic: {i[0]} {i[1]}")
            input_id = input("Which clinic's appointments would you like to see : ")
            clinic_ids = [clinic[0] for clinic in result]
            order = input('1.Reserved Appointments \n2.Cancelled Appointment  \n3.Increase Capacity \n4.Log Out \nPlease choose one option: ' )
            if order == "1":
                Employee.option_one()
                handle_backing_option()
            elif order == "2":
                Employee.option_two()
                handle_backing_option()
            elif order == "3":
                Employee.option_three()
                handle_backing_option()
            elif order == "4":
                users.logout(email)
                status = "0"
            else:
                print('Wrong input')

    elif status in ["11", "12", "13"]:
        handle_backing_option()
        