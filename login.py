from pathlib import Path
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pymysql
import credentials as cr
from signup_page import SignUp
import subprocess
import os

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./asserts")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

logged_in_username = None


class login_page:
    def __init__(self, root):
        self.window = root
        self.window.title("Log In")
        self.window.geometry("1280x800+0+0")
        self.window.config(bg="white")

        # Design part
        self.frame1 = Frame(self.window, bg="#323539")
        self.frame1.place(x=0, y=0, relwidth=0.5, relheight=1)

        # Load the background image for frame1
        try:
            self.bg_image_frame1 = Image.open(relative_to_assets("pexels-yifan-tang-94970673-13260043.jpg"))
            self.bg_photo_frame1 = None  # Initialize the photo image object
            self.bg_label_frame1 = Label(self.frame1)
            self.bg_label_frame1.place(x=0, y=0, relwidth=1, relheight=1)
            self.frame1.bind("<Configure>", self.resize_image_frame1)
            self.resize_image_frame1()
        except Exception as e:
            print(f"Error loading background image for frame1: {e}")

        # Entry Fields & Buttons
        self.frame2 = Frame(self.window, bg="white")
        self.frame2.place(x=640, y=0, relwidth=1, relheight=1)
        self.frame3 = Frame(self.frame2, bg="white")
        self.frame3.place(x=100, y=150, width=600, height=650)

        self.login_button_icon = PhotoImage(file=relative_to_assets("LOGIN.png"))
        self.create_account_button_icon = PhotoImage(file=relative_to_assets("Don't have an account Sign up.png"))

        # Title
        title = Label(self.frame3, text="WELCOME!!", font=("Arial", 30, "bold"), bg="white", fg="#323539")
        title.place(x=100, y=50)
        subtitle = Label(self.frame3, text="Please login to your account.", font=("Arial", 15), bg="white", fg="light grey")
        subtitle.place(x=100, y=95)

        # Email Label and Entry
        email_label = Label(self.frame3, text="Email Address", font=("Arial", 20, "bold"), bg="white", fg="#323539")
        email_label.place(x=100, y=170)
        self.email_entry = Entry(self.frame3, font=("Arial", 15), bg="white")
        self.email_entry.place(x=100, y=200, width=400, height=37)

        # Password Label and Entry
        password_label = Label(self.frame3, text="Password", font=("Arial", 20, "bold"), bg="white", fg="#323539")
        password_label.place(x=100, y=270)
        self.password_entry = Entry(self.frame3, font=("Arial", 15), bg="white", show="*")
        self.password_entry.place(x=100, y=300, width=400, height=37)

        # Login Button
        login_button = Button(self.frame3, image=self.login_button_icon, command=self.login_func)
        login_button.place(x=170, y=400, width=190, height=48)

        # Create New Account Button
        create_account_button = Button(self.frame3, image=self.create_account_button_icon, command=self.redirect_window)
        create_account_button.place(x=100, y=500, width=400, height=60)

    def resize_image_frame1(self, event=None):
        if self.bg_image_frame1:
            width = self.frame1.winfo_width()
            height = self.frame1.winfo_height()
            self.bg_image_resized_frame1 = self.bg_image_frame1.resize((width, height), Image.LANCZOS)
            self.bg_photo_frame1 = ImageTk.PhotoImage(self.bg_image_resized_frame1)
            self.bg_label_frame1.config(image=self.bg_photo_frame1)

    def login_func(self):
        global logged_in_username
        if self.email_entry.get() == "" or self.password_entry.get() == "":
            messagebox.showerror("Error!", "All fields are required", parent=self.window)
        else:
            try:
                connection = pymysql.connect(host=cr.host, user=cr.user, password=cr.password, database=cr.database)
                cur = connection.cursor()
                cur.execute("select * from user_register where email=%s and password=%s",
                            (self.email_entry.get(), self.password_entry.get()))
                row = cur.fetchone()

                if row is None:
                    messagebox.showerror("Error!", "Invalid USERNAME & PASSWORD", parent=self.window)
                else:
                    logged_in_username = self.email_entry.get()
                    with open("username.txt", "w") as file:
                        file.write(logged_in_username)
                    messagebox.showinfo("Success", "Welcome", parent=self.window)
                    self.window.destroy()
                    # Run blank.py
                    subprocess.run(["python", "main.py"])
            except Exception as e:
                messagebox.showerror("Error!", f"Error due to {str(e)}", parent=self.window)

    def redirect_window(self):

        self.window.destroy()

        subprocess.run(["python", "signup_page.py"])


if __name__ == "__main__":
    root = Tk()
    obj = login_page(root)
    root.mainloop()
