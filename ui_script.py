import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
from registration_script import RegistrationScript
from login_script import LoginScript

class MainUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Face Recognition System")
        self.root.geometry("800x600")

        # Apply a modern theme
        style = ThemedStyle(self.root)
        style.set_theme("plastik")

        # Create buttons for registration and login
        self.registration_button = ttk.Button(self.root, text="Register", command=self.open_registration, style="TButton")
        self.registration_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.LEFT)

        self.login_button = ttk.Button(self.root, text="Login", command=self.open_login, style="TButton")
        self.login_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.RIGHT)

        # Create a label or any other widgets to enhance your UI
        self.label = tk.Label(self.root, text="Welcome to Face Recognition System", font=("Helvetica", 16))
        self.label.pack(pady=20)

        # Create a back button (initially hidden)
        self.back_button = ttk.Button(self.root, text="Back to Main Menu", command=self.show_main_menu, style="TButton")
        self.back_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.LEFT)
        self.back_button.pack_forget()  # Initially hide the back button

    def open_registration(self):
        # Hide the main menu elements
        self.hide_main_menu()

        # Open the registration window
        self.registration_script = RegistrationScript(self.root, self.show_main_menu)
        self.registration_script.run()

    def open_login(self):
        # Hide the main menu elements
        self.hide_main_menu()

        # Open the login window
        self.login_script = LoginScript(self.root, self.show_main_menu)
        self.login_script.run()

    def show_main_menu(self):
        # Show the main menu elements
        self.show_main_menu_buttons()

        # Hide the registration and login script windows
        if hasattr(self, 'registration_script'):
            self.registration_script.on_closing()
        if hasattr(self, 'login_script'):
            self.login_script.on_closing()

    def hide_main_menu(self):
        # Hide the main menu elements
        self.registration_button.pack_forget()
        self.login_button.pack_forget()
        self.label.pack_forget()
        self.back_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.LEFT)

    def show_main_menu_buttons(self):
        # Show the main menu buttons
        self.registration_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.LEFT)
        self.login_button.pack(pady=20, padx=10, ipadx=5, ipady=5, side=tk.RIGHT)
        self.label.pack(pady=20)
        self.back_button.pack_forget()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    main_ui = MainUI()
    main_ui.run()
