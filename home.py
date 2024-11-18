from tkinter import Frame, Label, Button, Canvas
from PIL import Image, ImageTk
import psutil
import time

from pathlib import Path
import datetime

from login import logged_in_username
import base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import mimetypes
import pickle
import os
from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from tkinter import messagebox


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./asserts")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']

def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'API_KEY', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id,
                                                  body=message).execute()
        print('Message Id: {}'.format(message['id']))
        return message
    except Exception as e:
        print('An error occurred: {}'.format(e))
        return None

def create_message_with_attachment(sender, to, subject, message_text, file):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    (content_type, encoding) = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    (main_type, sub_type) = content_type.split('/', 1)

    if main_type == 'text':
        with open(file, 'rb') as f:
            msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)

    elif main_type == 'image':
        with open(file, 'rb') as f:
            msg = MIMEImage(f.read(), _subtype=sub_type)

    elif main_type == 'audio':
        with open(file, 'rb') as f:
            msg = MIMEAudio(f.read(), _subtype=sub_type)

    else:
        with open(file, 'rb') as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())

    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment',
                   filename=filename)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

# Define the function to send an emergency email
def send_emergency_email():
    try:
        # Get the Gmail service
        service = get_service()
        user_id = 'me'

        # Create the message with attachment
        msg = create_message_with_attachment('GMAIL_USER', 'GMAIL_USER',
                                             'Emergency Alert', 'Emergency situation detected!', './sample_file.txt')

        # Send the message
        send_message(service, user_id, msg)

        # Show success message
        messagebox.showinfo("Success", "Emergency email sent successfully!")

    except Exception as e:
        # Show error message
        messagebox.showerror("Error", f"An error occurred: {e}")

def get_logged_in_username():
    try:
        with open("username.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Unknown User"
class HomePage(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.config(bg="#FFFFFF")
        logged_in_username = get_logged_in_username()

        # Frame for user information and stats on the right
        self.frame1 = Frame(self, bg="#F0F0F0")
        self.frame1.place(x=0, y=0, width=1500, height=80)

        # Load and display the image in frame1
        image_path = relative_to_assets('profile_3135715.png')  # replace 'your_image.png' with the actual image filename
        image = Image.open(image_path)
        image = image.resize((60, 60), Image.Resampling.LANCZOS)  # Use the updated resampling filter
        self.image_tk = ImageTk.PhotoImage(image)
        self.image_label = Label(self.frame1, image=self.image_tk, bg="#F0F0F0")
        self.image_label.place(x=1140, y=7)
        username_label = Label(self.frame1, text=f" {logged_in_username}", font=("Georgia", 25),
                               bg="#F0F0F0", fg="#323539")
        username_label.place(x=890, y=17)


        # Frame for user information and stats on the right
        self.frame2 = Frame(self, bg="white")
        self.frame2.place(x=80, y=150, width=1000, height=300)
        # Add text for emergency instructions
        title = Label(self.frame2, text="In case of emergency", font=("Georgia", 30, "bold"), bg="white", fg="#526D82")
        title.place(x=0, y=20)
        title = Label(self.frame2, text="By pressing the 'Emergency Alert', an automated email will be dispatched, ", font=("Georgia", 20), bg="white", fg="#9DB2BF")
        title.place(x=0, y=65)
        title = Label(self.frame2, text="signaling the urgency of the situation. This ensures that necessary measures  ",
                      font=("Georgia", 20), bg="white", fg="#9DB2BF")
        title.place(x=0, y=95)
        title = Label(self.frame2, text=" can be taken promptly, facilitating a rapid response. ",
                      font=("Georgia", 20), bg="white", fg="#9DB2BF")
        title.place(x=0, y=125)

        # Load the image
        emergency_image = Image.open(relative_to_assets("Untitled design.png"))  # Replace "emergency_icon.png" with the actual image file path
        emergency_image = emergency_image.resize((270, 90), Image.LANCZOS)  # Resize the image with LANCZOS filter
        emergency_icon = ImageTk.PhotoImage(emergency_image)

        # Emergency Alert button with image
        emergency_button = Button(self.frame2,
                                  compound="left", image=emergency_icon, height=70, width=250,
                                  command=send_emergency_email)
        emergency_button.place(x=750, y=50)
        emergency_button.image = emergency_icon





        # Define colors for the canvases
        colors = ["#526D82", "#9DB2BF", "#DDE6ED", "#526D82", "#9DB2BF", "#DDE6ED"]

        # Create 6 canvases in 2 rows and 3 columns
        self.canvases = []
        canvas_width = 350
        canvas_height = 150
        padding_x = 35
        padding_y = 35

        for i in range(2):  # 2 rows
            for j in range(3):  # 3 columns
                x = 50 + j * (canvas_width + padding_x)
                y = 470 + i * (canvas_height + padding_y)

                canvas_color = colors[i * 3 + j]  # Select color based on the index
                canvas = Canvas(self, bg="#FFFFFF", bd=0, highlightthickness=0, relief='ridge')
                canvas.place(x=x, y=y, width=canvas_width, height=canvas_height)

                # Draw rounded rectangle on each canvas
                self.draw_rounded_rectangle(canvas, 0, 0, canvas_width, canvas_height, 35, fill=canvas_color, outline="")



                self.canvases.append(canvas)

        # Add CPU, Memory, and Disk usage labels to the first row canvases
        self.cpu_label = Label(self.canvases[0], bg=colors[0], fg = "#212A3E", font=("Georgia", 35))
        self.cpu_label.place(x=20, y=60)
        self.memory_label = Label(self.canvases[1], bg=colors[1],fg = "#212A3E", font=("Georgia", 30))
        self.memory_label.place(x=20, y=60)
        self.disk_label = Label(self.canvases[2], bg=colors[2],fg = "#212A3E", font=("Georgia", 30))
        self.disk_label.place(x=20, y=60)

        # Add time and date labels to the empty canvas block
        self.time_label = Label(self.canvases[3], bg=colors[3],fg = "#212A3E", font=("Georgia", 30))
        self.time_label.place(x=20, y=60)
        self.date_label = Label(self.canvases[4], bg=colors[4],fg = "#212A3E", font=("Georgia", 30))
        self.date_label.place(x=20, y=60)
        self.uptime_label = Label(self.canvases[5], bg=colors[5],fg = "#212A3E", font=("Georgia", 22))
        self.uptime_label.place(x=20, y=60)

        # Start updating the system usage labels
        self.update_system_usage()

        # Start updating the time and date labels
        self.update_time_date()

    def draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=35, **kwargs):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def get_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        return f"CPU Usage: {cpu_usage}%"

    def get_memory_usage(self):
        memory_usage = psutil.virtual_memory().percent
        return f"Memory Usage: {memory_usage}%"

    def get_disk_space(self):
        disk_space = psutil.disk_usage('/').percent
        return f"Disk Space: {disk_space}%"

    def get_system_uptime(self):
        boot_time_seconds = psutil.boot_time()
        current_time_seconds = time.time()
        uptime_seconds = current_time_seconds - boot_time_seconds

        # Convert uptime from seconds to a more human-readable format
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
        return f"System Uptime: {uptime_str}"

    def update_system_usage(self):
        self.cpu_label.config(text=self.get_cpu_usage())
        self.memory_label.config(text=self.get_memory_usage())
        self.disk_label.config(text=self.get_disk_space())
        # Update system uptime label
        self.uptime_label.config(text=self.get_system_uptime())

        # Update every 1000 ms (1 second)
        self.after(1000, self.update_system_usage)

    def update_time_date(self):
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%Y-%m-%d")
        self.time_label.config(text=f"Time: {current_time}")
        self.date_label.config(text=f"Date: {current_date}")
        self.after(1000, self.update_time_date)

