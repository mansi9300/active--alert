import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
from pathlib import Path
from ultralytics import YOLO
from dotenv import load_dotenv
import cvzone
import math

from home import HomePage

from tkinter import Tk, Frame, Canvas, Button, PhotoImage, StringVar, Label, messagebox, NW
from PIL import Image, ImageTk
import time
import cv2

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



OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./asserts")
def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

SCOPES = ['https://mail.google.com/']


load_dotenv()

api_key = os.getenv("API_KEY")
gmail_user = os.getenv("GMAIL_USER")

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'API_KEY', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
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
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

def send_emergency_email(screenshot_path):
    try:
        service = get_service()
        user_id = 'me'
        msg = create_message_with_attachment(
            'GMAIL_USER', 'GMAIL_USER',
            'Emergency Alert', 'suspicious weapon detected', screenshot_path
        )
        send_message(service, user_id, msg)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
# Function to play voice alert


class DesktopApp(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title("Active Alert ")
        self.attributes("-fullscreen", True)  # Make the window fullscreen

        self.configure(bg="#5E95FF")

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the dimensions of the canvas
        self.canvas_width = screen_width
        self.canvas_height = screen_height

        self.current_window = None
        self.current_window_label = StringVar()

        self.canvas = Canvas(
            self,
            bg="#323539",
            height=self.canvas_height,
            width=self.canvas_width + 1000,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        self.canvas.place(x=0, y=0)

        # Draw the white background
        self.canvas.create_rectangle(
            215, 0.0, self.canvas_width, self.canvas_height, fill="#FFFFFF", outline=""
        )

        # Load the image and place it on the canvas
        try:
            self.image = PhotoImage(file=relative_to_assets("active copy.png"))  # Replace with your image path
            self.canvas.create_image(5, 25, anchor=NW, image=self.image)
        except Exception as e:
            print(f"Error loading image: {e}")

        self.sidebar_indicator = self.canvas.create_rectangle(
            0, 0, 7, 47, fill="white", outline=""
        )



        self.button_images = []  # Store button images as instance variables

        try:
            button_image_1 = PhotoImage(file=relative_to_assets("Add a heading/1.png"))  # Replace with the path to your first image
            button_image_2 = PhotoImage(file=relative_to_assets("Add a heading/2.png"))  # Replace with the path to your second image
            button_image_3 = PhotoImage(file=relative_to_assets("Add a heading/3.png"))  # Replace with the path to your third image
            # For simplicity, we'll reuse the same three images for the last two buttons
            button_image_4 = PhotoImage(file=relative_to_assets("Add a heading/4.png"))
            button_image_5 = PhotoImage(file=relative_to_assets("Add a heading/5.png"))
            button_image_6 = PhotoImage(file=relative_to_assets("Add a heading/6.png"))
            self.button_images.extend([button_image_1, button_image_2, button_image_3, button_image_4, button_image_5, button_image_6])
        except Exception as e:
            print("Error loading image:", e)

        buttons = [
            {"text": "Home", "image": self.button_images[0], "command": lambda: self.handle_btn_press("Home")},
            {"text": "Start Recording", "image": self.button_images[1], "command": self.start_recording},
            {"text": "Stop Recording", "image": self.button_images[2], "command": self.stop_recording},
            {"text": "Records", "image": self.button_images[3], "command": lambda: self.handle_btn_press("Records")},
            {"text": "About Us", "image": self.button_images[4], "command": lambda: self.handle_btn_press("About Us")},
            {"text": "Log out", "image": self.button_images[5], "command": lambda: self.handle_btn_press("Log out")},
            # Add more buttons as needed
        ]

        self.sidebar_buttons = []
        button_height = 47.0  # Height of each button
        num_buttons = len(buttons)  # Total number of buttons

        for i, button_data in enumerate(buttons):
            if i == num_buttons - 1:  # If it's the last button, place it at the bottom
                y_position = self.canvas_height - (num_buttons * button_height) + i * button_height-40
            else:
                y_position = 220.0 + i * button_height

            button = Button(
                self,
                image=button_data["image"],
                borderwidth=0,
                highlightthickness=0,
                text=button_data["text"],  # Set the text of the button
                command=button_data["command"],
                cursor='hand2',
                activebackground="#DDDDDD",
                relief="flat",
            )
            button.place(x=7.0, y=y_position, width=208.0, height=button_height)
            self.sidebar_buttons.append(button)



        self.windows = {
            "Home": Frame(self.canvas, bg="#FFFFFF"),  # Change "Room" to "Start Recording"
            "Start Recording": Frame(self.canvas, bg="#FFFFFF"),  # Change "Guest" to "Stop Recording"
            "Stop Recording": Frame(self.canvas, bg="#FFFFFF"),
            "Records": Frame(self.canvas, bg="#FFFFFF"),
            "About Us": Frame(self.canvas, bg="#FFFFFF"),
            "Log out": Frame(self.canvas, bg="#FFFFFF"),
            # Add more frames for additional windows
        }

        # Add the home page frame
        self.home_page_frame = HomePage(self.canvas)

        self.handle_btn_press("Home")  # Set "Home" as default
        self.resizable(False, False)

        self.cap = None  # Camera capture object
        self.is_recording = False  # Flag to check if recording is on

        self.video_label = Label(self.windows["Start Recording"], bg="#FFFFFF")
        self.video_label.pack(fill="both", expand=True)

        self.first_frame_processed = False

        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

        self.thumbnail_dir = "thumbnails"
        if not os.path.exists(self.thumbnail_dir):
            os.makedirs(self.thumbnail_dir)

        self.load_thumbnails()

        #yolo model

        self.model = YOLO("best.pt")

        self.classNames = ['Grenade', 'Gun', 'Knife', 'Pistol', 'handgun', 'rifle']


    def handle_btn_press(self, name):
        # Place the sidebar indicator on the respective button
            for button in self.sidebar_buttons:
                  button.configure(bg="#DDDDDD")  # Reset background color

            selected_button_index = list(self.windows.keys()).index(name)
            self.sidebar_buttons[selected_button_index].configure(bg="#FFFFFF")  # Highlight selected button
            button_y = self.sidebar_buttons[selected_button_index].winfo_y()
            self.canvas.coords(self.sidebar_indicator, 0, button_y, 7, button_y + 47)

            # Hide all frames
            for window in self.windows.values():
                window.place_forget()

            # Show the frame of the button pressed
            self.current_window = self.windows.get(name)
            if self.current_window:
                self.current_window.place(x=215, y=0, width=self.canvas_width - 215, height=self.canvas_height)

            # Show or hide the home page frame based on the button pressed
            if name == "Home":
                self.home_page_frame.place(x=215, y=0, width=self.canvas_width - 215, height=self.canvas_height)
            else:
                self.home_page_frame.place_forget()


            # Load and display images when the "About Us" button is clicked
            if name == "About Us":
                try:
                    # Load images
                    image1 = PhotoImage(file=relative_to_assets("about/3.png"))  # Replace "path_to_image1.png" with your image path
                    image2 = PhotoImage(file=relative_to_assets("about/2.png"))  # Replace "path_to_image2.png" with your image path
                    image3 = PhotoImage(file=relative_to_assets("about/1.png") ) # Replace "path_to_image3.png" with your image path

                    # Create labels to display images
                    label1 = Label(self.windows["About Us"], image=image1, bg="#FFFFFF")
                    label2 = Label(self.windows["About Us"], image=image2, bg="#FFFFFF")
                    label3 = Label(self.windows["About Us"], image=image3, bg="#FFFFFF")

                    # Position the labels
                    label1.place(x=50, y=50)  # Adjust coordinates as needed
                    label2.place(x=50, y=300)  # Adjust coordinates as needed
                    label3.place(x=50, y=570)  # Adjust coordinates as needed

                    # Keep references to images to prevent garbage collection
                    label1.image = image1
                    label2.image = image2
                    label3.image = image3
                except Exception as e:
                    print("Error loading images:", e)

               # Close the application when "Log out" button is clicked
            if name == "Log out":
                self.destroy()

    def start_recording(self):
        self.handle_btn_press("Start Recording")
        if not self.is_recording:
            self.is_recording = True
            if self.cap is None or not self.cap.isOpened():  # Check if camera is not already open
                self.cap = cv2.VideoCapture(0)  # Use the default camera
                if not self.cap.isOpened():
                    print("Error: Could not open camera.")
                    self.is_recording = False
                    return
                print("Camera opened successfully in start_recording")
            else:
                print("Camera already open in start_recording")
            self.update_camera_feed()

    def stop_recording(self):
        self.handle_btn_press("Stop Recording")
        if self.is_recording:
            self.is_recording = False
            if self.cap is not None:
                self.cap.release()
            self.video_label.config(image='')

            # After stopping recording, switch to "Home" window
            self.handle_btn_press("Home")

    def update_camera_feed(self):
        try:
            print("update_camera_feed called")
            if self.is_recording:
                if self.cap is None or not self.cap.isOpened():
                    print("Camera not open in update_camera_feed")
                else:
                    print("Camera is open in update_camera_feed")
                    ret, frame = self.cap.read()
                    if ret:
                        results = self.model(frame, device="mps")
                        print("YOLO detection performed")
                        for r in results:
                            boxes = r.boxes
                            for box in boxes:
                                x1, y1, x2, y2 = box.xyxy[0]
                                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                                w, h = x2 - x1, y2 - y1
                                cvzone.cornerRect(frame, (x1, y1, w, h))
                                conf = math.ceil((box.conf[0] * 100)) / 100
                                cls = int(box.cls[0])
                                label = self.classNames[cls]
                                cvzone.putTextRect(frame, f'{label} {conf}', (max(0, x1), max(35, y1)), scale=1,
                                                   thickness=1)

                                # Save screenshots and thumbnails only if confidence is above 60
                                if not self.first_frame_processed and conf > 0.6 and label in self.classNames:
                                    # Save full-size screenshot
                                    screenshot_path = os.path.join(self.screenshot_dir,
                                                                   f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png")
                                    cv2.imwrite(screenshot_path, frame)

                                    # Save minimized screenshot for records
                                    thumbnail_path = os.path.join(self.thumbnail_dir,
                                                                  f"thumbnail_{time.strftime('%Y%m%d_%H%M%S')}.png")
                                    thumbnail = cv2.resize(frame, (100, 100))  # Resize to a smaller size
                                    cv2.imwrite(thumbnail_path, thumbnail)

                                    # Display the thumbnail in the "Records" window
                                    self.add_thumbnail_to_records(thumbnail_path)


                                    self.first_frame_processed = True
                                    send_emergency_email(screenshot_path)# Set the flag to indicate first frame processed

                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame)
                        imgtk = ImageTk.PhotoImage(image=img)
                        self.video_label.imgtk = imgtk
                        self.video_label.configure(image=imgtk)
                    else:
                        print("Failed to capture frame")
                self.video_label.after(10, self.update_camera_feed)
        except Exception as e:
            print(f"Error in update_camera_feed: {e}")

    def add_thumbnail_to_records(self, thumbnail_path):
        try:
            thumbnail_img = Image.open(thumbnail_path)
            thumbnail_imgtk = ImageTk.PhotoImage(thumbnail_img)

            # Get the current number of thumbnails
            num_thumbnails = len(self.windows["Records"].winfo_children())
            row = num_thumbnails // 10  # Adjust number of thumbnails per row as needed
            column = num_thumbnails % 10

            record_label = Label(self.windows["Records"], image=thumbnail_imgtk, bg="#FFFFFF")
            record_label.image = thumbnail_imgtk  # Keep a reference to prevent garbage collection
            record_label.grid(row=row, column=column, padx=10, pady=10)  # Adjust the grid layout
        except Exception as e:
            print(f"Error adding thumbnail to records: {e}")

    def load_thumbnails(self):
        try:
            # Clear existing thumbnails
            for widget in self.windows["Records"].winfo_children():
                widget.destroy()

            # Load thumbnails from the thumbnail directory
            for filename in os.listdir(self.thumbnail_dir):
                if filename.endswith(".png"):
                    thumbnail_path = os.path.join(self.thumbnail_dir, filename)
                    self.add_thumbnail_to_records(thumbnail_path)

        except Exception as e:
            print(f"Error loading thumbnails: {e}")

def start_application():
    print("Starting application...")
    app = DesktopApp()
    app.mainloop()

if __name__ == "__main__":
    start_application()  # Call the function when main.py is executed directly
