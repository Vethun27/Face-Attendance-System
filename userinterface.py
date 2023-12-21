import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
from datetime import datetime
import constants



class App:
    def __init__(self):
        ctk.set_appearance_mode(constants.appApperanceMode)
        ctk.set_default_color_theme(constants.appDefaultColorTheme)
        self.root = ctk.CTk()
        self.root.geometry(constants.appGeometry + constants.appPosition)
        self.root.resizable(width=False, height=False)
        self.root.title(constants.appTitle)
        self.loggedIn = False
        self.cap = cv2.VideoCapture(0)

        self.buildFrontend_sidebar()
        self.buildFrontend_mainFrame()
        self.takeAttendance_btn.invoke()  #starts the take Attendancy directly after App start



    def buildFrontend_sidebar(self):
        self.option_frame = ctk.CTkFrame(self.root, fg_color='#292727', bg_color='#292727')
        self.option_frame.pack(side=ctk.LEFT)
        self.option_frame.pack_propagate(False)
        self.option_frame.configure(height=620, width=100)

        self.takeAttendance_btn =  ctk.CTkButton(self.option_frame, text='Take\nAttendancy', font=('Bold', 15), fg_color='#292727', bg_color='#292727', text_color='#158aff', hover_color='#333232', corner_radius=0, border_width=0, width=100, height=35,command=lambda:self.indicate(self.takeAttendance_indicate, self.takeAttendace_page)) 
        self.takeAttendance_btn.pack(pady=20)
        self.takeAttendance_btn.configure(state="normal")
        self.takeAttendance_indicate =  ctk.CTkLabel(self.option_frame, text='', bg_color='#595757', width=5, height=40)
        self.takeAttendance_indicate.place(x=3, y=20)


    def buildFrontend_mainFrame(self):
        self.main_frame = ctk.CTkFrame(self.root, border_color='black', border_width=5)
        self.main_frame.pack(side=ctk.LEFT)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(height=620, width=1100)
        

    def delete_frameContent(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()

    def hide_indicators(self):
        self.takeAttendance_indicate.configure(bg_color='#c3c3c3')
        

    def indicate(self, lb, page):
        self.hide_indicators()
        lb.configure(bg_color='#158aff')
        self.delete_frameContent()
        page()


    def start_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("Start Working... Time: " + formatted_timestamp)

    def end_working(self):
        timestamp = datetime.now()
        formatted_timestamp = timestamp.strftime("%d.%m.%Y %H:%M:%S")
        print("End Working... Time: " + formatted_timestamp)

    def takeAttendace_page(self):
        self.takeAttendace_frame = ctk.CTkFrame(self.main_frame)
        self.takeAttendace_frame.pack(pady=20, padx=20, side=ctk.TOP, anchor="nw")
        cam_lb = ctk.CTkLabel(self.takeAttendace_frame, text='')
        cam_lb.pack(side=ctk.LEFT)
        self.add_webcam(cam_lb)

        start_work_btn = ctk.CTkButton(self.takeAttendace_frame, text="Start Work", bg_color='green', fg_color='green', hover_color='#2b5c30', width=500, height = 260, command=lambda:self.start_working())
        start_work_btn.pack(side=ctk.TOP, pady=15, padx= 20)

        end_work_btn = ctk.CTkButton(self.takeAttendace_frame, text="End Work", bg_color='red', hover_color='#5c1d1d', fg_color='red', width=500, height = 260, command=lambda:self.end_working())
        end_work_btn.pack(side=ctk.TOP, anchor='s', pady=15, padx= 20)



    def add_webcam(self, label):
        self.process_webcam(label)

    def process_webcam(self, label):
        ret, frame = self.cap.read()

        if(ret):
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            imgctk = ctk.CTkImage(dark_image=Image.fromarray(img_), size=(800, 620))
            label.configure(image=imgctk)
            label.after(20, self.process_webcam, label)
        else:
            print("Error in reading Camera")

    def start(self):
        self.root.mainloop()




if __name__ == "__main__":
    app = App()
    app.start()



