import tkinter as tk
from tkinter import messagebox, scrolledtext
import pymysql
from datetime import datetime

# Constants
ROOM_COST_PER_DAY = 1200


# Initialize available rooms
available_rooms = list(range(1, 11))
checked_in_guests = []  # To store guest information

class HotelManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.config(bg='#87A2FF')

        scrn_width = self.root.winfo_screenwidth()
        scrn_height = self.root.winfo_screenheight()

        self.root.geometry(f"{scrn_width}x{scrn_height}+0+0")

        mainTitle = tk.Label(self.root,text='Hotel Management System',bg='#C4D7FF',fg='black',bd=5,relief='groove',font=('Times New Roman',30,'bold'))
        mainTitle.pack(side="top",fill='x')

        # Create a scrolled text area for displaying guest information
        self.guest_info_display = scrolledtext.ScrolledText(root, width=60, height=20, state='disabled')
        self.guest_info_display.pack(pady=10)


        # Create buttons
        btn_fetch_rooms = tk.Button(root, text="Fetch Available Room Data", command=self.fetch_available_rooms,bg='#FFD7C4',font=('Times New Roman',15,'bold'))
        btn_check_in = tk.Button(root, text="Check In", command=self.check_in,bg='#FFD7C4',font=('Times New Roman',15,'bold'))
        btn_check_out = tk.Button(root, text="Check Out", command=self.check_out,bg='#FFD7C4',font=('Times New Roman',15,'bold'))
        btn_show_guest_list = tk.Button(root, text="Show All Guest List", command=self.show_guest_list,bg='#FFD7C4',font=('Times New Roman',15,'bold'))
        btn_show_history = tk.Button(root, text="Show Guest History", command=self.show_guest_history,bg='#FFD7C4',font=('Times New Roman',15,'bold'))

        # Arrange buttons in the window
        btn_fetch_rooms.pack(pady=10)
        btn_check_in.pack(pady=10)
        btn_check_out.pack(pady=10)
        btn_show_guest_list.pack(pady=10)
        btn_show_history.pack(pady=10)

    def fetch_available_rooms(self):
        if available_rooms:
            messagebox.showinfo("Fetch Available Rooms", f"Available Rooms: {available_rooms}")
        else:
            messagebox.showinfo("Fetch Available Rooms", "No rooms available.")

    def check_in(self):
        def submit():
            name = entry_name.get()
            phone = entry_phone.get()
            gender = entry_gender.get()
            email = entry_email.get()
            days = entry_guests.get()

            if not name or not phone or gender == "Select" or not email or not days.isdigit():
                messagebox.showwarning("Input Error", "Please fill in all fields correctly.")
                return
            if not available_rooms:   
                messagebox.showwarning("No Rooms Available", "No available rooms to check in.")
                return
            
            room_number = available_rooms.pop(0)  # Assign the first available room
            total_cost = ROOM_COST_PER_DAY * int(days)  # Calculate total cost
            
            # Insert guest information into the database
            self.db_connect(name, phone, gender, email, days, room_number, total_cost)

            self.update_guest_info_display()  # Update display after check-in
            messagebox.showinfo("Check In", f"Check-in Successful!\nRoom Number: {room_number}\nTotal Bill Amount: ₹{total_cost}")
            check_in_window.destroy()  # Close the popup after submission

        # Create a new popup window
        check_in_window = tk.Toplevel(self.root)
        check_in_window.title("Check In")

        # Create input fields
        tk.Label(check_in_window, text="Guest Name:").pack()
        entry_name = tk.Entry(check_in_window)
        entry_name.pack()

        tk.Label(check_in_window, text="Phone Number:").pack()
        entry_phone = tk.Entry(check_in_window)
        entry_phone.pack()

        # Gender selection using a dropdown menu
        tk.Label(check_in_window, text="Gender:").pack()
        entry_gender = tk.StringVar(check_in_window)
        entry_gender.set("Select")  # Default value
        gender_menu = tk.OptionMenu(check_in_window, entry_gender, "Male", "Female", "Other")
        gender_menu.pack()

        tk.Label(check_in_window, text="Email:").pack()
        entry_email = tk.Entry(check_in_window)
        entry_email.pack()

        tk.Label(check_in_window, text="Number of days you will stay:").pack()
        entry_guests = tk.Entry(check_in_window)
        entry_guests.pack()

        # Submit button
        btn_submit = tk.Button(check_in_window, text="Submit", command=submit)
        btn_submit.pack(pady=10)

    def check_out(self):
        def confirm_checkout():
            selected_guest = guest_var.get()
            if selected_guest == "Select Guest":
                messagebox.showwarning("Select Guest", "Please select a guest to check out.")
                return

            # Find guest in the list and remove them
            for guest in checked_in_guests:
                if guest["name"] == selected_guest:
                    # Move guest data to checked_out_guests table
                    self.move_to_checked_out(guest)

                    available_rooms.append(guest["room"])  # Free up the room
                    checked_in_guests.remove(guest)  # Remove guest from the list
                    self.update_guest_info_display()  # Update display after check-out
                    messagebox.showinfo("Check Out", f"Checked out {selected_guest} from Room {guest['room']}.")
                    break
            else:
                messagebox.showwarning("Checkout Error", "Guest not found.")
            
            checkout_window.destroy()

        # Create a new popup window for checkout
        checkout_window = tk.Toplevel(self.root)
        checkout_window.title("Check Out")

        tk.Label(checkout_window, text="Select Guest to Check Out:").pack()

        # Dropdown for selecting guest
        guest_var = tk.StringVar(checkout_window)
        guest_var.set("Select Guest")  # Default value
        guest_names = [guest['name'] for guest in checked_in_guests] + ["Select Guest"]
        guest_menu = tk.OptionMenu(checkout_window, guest_var, *guest_names)
        guest_menu.pack()

        # Confirm checkout button
        btn_confirm = tk.Button(checkout_window, text="Confirm Check Out", command=confirm_checkout)
        btn_confirm.pack(pady=10)

    def show_guest_list(self):
        try:
            con = pymysql.connect(host='localhost', user='root', passwd='Abhi@8340', database='hotel')
            cur = con.cursor()
            cur.execute("SELECT * FROM guests")
            guest_data = cur.fetchall()
            con.close()

            self.guest_info_display.configure(state='normal')  # Allow editing
            self.guest_info_display.delete(1.0, tk.END)  # Clear existing text

            if not guest_data:
                self.guest_info_display.insert(tk.END, "No guests currently checked in.")
            else:
                for row in guest_data:
                    guest_details = (f"Name: {row[1]}\n"
                                     f"Phone: {row[2]}\n"
                                     f"Gender: {row[3]}\n"
                                     f"Email: {row[4]}\n"
                                     f"Days: {row[5]}\n"
                                     f"Room: {row[6]}\n"
                                     f"Total Bill: ₹{row[7]}\n"
                                     f"{'='*30}\n")
                    self.guest_info_display.insert(tk.END, guest_details)

            self.guest_info_display.configure(state='disabled')  # Make the text area read-only
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def show_guest_history(self):
        try:
            con = pymysql.connect(host='localhost', user='root', passwd='Abhi@8340', database='hotel')
            cur = con.cursor()
            cur.execute("SELECT * FROM checked_out_guests")
            history = cur.fetchall()
            con.close()

            if not history:
                messagebox.showinfo("Guest History", "No guests have checked out yet.")
                return

            history_info = "\n".join([f"Name: {row[1]}, Phone: {row[2]}, Gender: {row[3]}, "
                                      f"Email: {row[4]}, Days: {row[5]}, Room: {row[6]}, "
                                      f"Total Bill: ₹{row[7]}, Checkout Date: {row[8]}"
                                      for row in history])
            messagebox.showinfo("Guest History", f"Checked Out Guests:\n{history_info}")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def update_guest_info_display(self):
        self.guest_info_display.configure(state='normal')  # Allow editing
        self.guest_info_display.delete(1.0, tk.END)  # Clear existing text
        
        if not checked_in_guests:
            self.guest_info_display.insert(tk.END, "No guests currently checked in.")
        else:
            for guest in checked_in_guests:
                guest_details = (f"Name: {guest['name']}\n"
                                 f"Phone: {guest['phone']}\n"
                                 f"Gender: {guest['gender']}\n"
                                 f"Email: {guest['email']}\n"
                                 f"Days: {guest['days']}\n"
                                 f"Room: {guest['room']}\n"
                                 f"Total Bill: ₹{guest['total_cost']}\n"
                                 f"{'='*30}\n")
                self.guest_info_display.insert(tk.END, guest_details)
        
        self.guest_info_display.configure(state='disabled')  # Make the text area read-only

    # Database connection and insertion function
    def db_connect(self, name, phone, gender, email, days, room_number, total_cost):
        try:
            con = pymysql.connect(host='localhost', user='root', passwd='Abhi@8340', database='hotel')
            cur = con.cursor()
            cur.execute('''
            INSERT INTO guests (name, phone, gender, email, days, room_number, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''', (name, phone, gender, email, days, room_number, total_cost))
            con.commit()
            con.close()
            checked_in_guests.append({
                "name": name,
                "phone": phone,
                "gender": gender,
                "email": email,
                "days": days,
                "room": room_number,
                "total_cost": total_cost
            })
            messagebox.showinfo("Success", "Guest information saved successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def move_to_checked_out(self, guest):
        try:
            con = pymysql.connect(host='localhost', user='root', passwd='Abhi@8340', database='hotel')
            cur = con.cursor()
            cur.execute('''
            INSERT INTO checked_out_guests (name, phone, gender, email, days, room_number, total_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            ''', (guest["name"], guest["phone"], guest["gender"], guest["email"],
                  guest["days"], guest["room"], guest["total_cost"]))
            con.commit()
            con.close()
            messagebox.showinfo("Success", "Guest checked out successfully.")
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

# Create the main application
if __name__ == "__main__":
    root = tk.Tk()
    app = HotelManagement(root)
    root.mainloop()
