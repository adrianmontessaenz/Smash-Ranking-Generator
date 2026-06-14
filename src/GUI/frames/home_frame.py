from tkinter import *
import customtkinter as ctk
import GUI.window as window
from ranking.data_manager import DataManager
from ranking.compute_ranking import compute_ranking

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, data_manager : DataManager):
        super().__init__(master)
        
        # Main frame for the home frame
        self.pack(fill="both", expand=True)
        self.data_manager = data_manager
        
        # Add frames
        self.left_frame = _LeftFrame(self)
        self.middle_frame = _MiddleFrame(self)
        self.right_frame = _RightFrame(self)
        
# Left frame class
class _LeftFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="y")
        self.configure(width=300)
        
        # Add frame title
        self.title_label = ctk.CTkLabel(self, text="Options", font=ctk.CTkFont(size=25, weight="bold"), wraplength=200)
        self.title_label.pack(padx=15, pady=20)
        
        # Add buttons for navigation
        self.button1 = ctk.CTkButton(self, text="Tournament Data", command=master.master._show_tournament_data_frame)
        self.button1.pack(padx=15, pady=10)
        
        self.button2 = ctk.CTkButton(self, text="Player Data", command=master.master._show_player_data_frame)
        self.button2.pack(padx=15, pady=10)
        
        self.button3 = ctk.CTkButton(self, text="Ranking Rules", command=master.master._show_ranking_rules_frame)
        self.button3.pack(padx=15, pady=10)
        
        self.button4 = ctk.CTkButton(self, text="Generate Ranking", command=self.compute_ranking)
        self.button4.pack(padx=15, pady=10)
        
        # Set StartGG developer api key
        self.api_key_label = ctk.CTkLabel(self, text="StartGG API Key:", font=ctk.CTkFont(size=12, weight="bold"))
        self.api_key_label.pack(padx=15, pady=(20,5))
        self.api_key_entry = ctk.CTkEntry(self, width=150, placeholder_text="Enter your StartGG API Key")
        if master.data_manager.get_api_key():
            self.api_key_entry.insert(0, master.data_manager.get_api_key())
        self.api_key_entry.pack(padx=5, pady=(0,20))
        self.api_key_button = ctk.CTkButton(self, text="Save API Key", command=self._save_api_key)
        self.api_key_button.pack(padx=15, pady=(0,20))
        
        # Add appearance mode options
        self.appearance_mode_optionmenu = ctk.CTkOptionMenu(self, values=["Light", "Dark"], variable= ctk.StringVar(value="Dark"), command=self._change_appearance_mode)
        self.appearance_mode_optionmenu.pack(side="bottom", padx=15, pady=(0,30))
        self.appearance_mode_label = ctk.CTkLabel(self, text="Appearance Mode:", font=ctk.CTkFont(size=12, weight="bold"))
        self.appearance_mode_label.pack(side="bottom", padx=15, pady=(0,5))
        
    def _change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)
        
    def _save_api_key(self):
        api_key = self.api_key_entry.get()
        self.master.data_manager.save_api_key(api_key)
        
    def compute_ranking(self):
        # Call the compute ranking method
        compute_ranking(self.master.data_manager)
        
        
class _MiddleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent")
        self.title_label = ctk.CTkLabel(self, text="Ranking Generator", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Add scrollable text box for welcome message
        self.textbox = ctk.CTkTextbox(self, width=600, height=275, wrap="word")
        self.textbox.pack(pady=10)
        welcome_message = (
            "Welcome to the Ranking Generator Application!\n\n"
            "This application is designed to generate the rankings for your region, allowing you to manage\n"
            "the tournaments you want to include, players that count extra points in the ranking, and rules\n"
            "such as tournament values and more.\n\n"
            "Use the options on the left to navigate through the different sections of the application.\n"            
        )
        self.textbox.insert("0.0", welcome_message)
        self.textbox.configure(state="disabled")

class _RightFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="right", fill="y")
        self.configure(width=300)
        
        # Add frame title
        self.title_label = ctk.CTkLabel(self, text="Info", font=ctk.CTkFont(size=25, weight="bold"), wraplength=200)
        self.title_label.pack(padx=15, pady=10)
        
        # Add additional info widgets here
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        self.tabview.add("Tournaments")
        self.tabview.add("Players")
        self.tabview.add("Rules")