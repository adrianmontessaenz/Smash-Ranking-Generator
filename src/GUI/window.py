from tkinter import *
import customtkinter
import GUI.frames.home_frame as home_frame
import GUI.frames.tournament_frame as tournament_frame
import GUI.frames.player_frame as player_frame
from ranking.data_manager import DataManager

class AppWindow(customtkinter.CTk):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        
        self.data_manager = data_manager
        
        # Set appearance mode
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")
        
        # Edit window parameters
        self.title("Ranking Generator Application")
        self.minsize(1000, 500)
        self.maxsize(1000, 500)
        self.geometry("1000x500")
        
        # Initialize home frame
        self._show_home_frame()
    
    def _clear_frame(self):
        # Clear all widgets from the root window
        for widget in self.winfo_children():
            widget.destroy()
        
    def _show_home_frame(self):
        # Clear current frame and show home frame
        self._clear_frame()
        self.frame = home_frame.HomeFrame(self, self.data_manager)
        
    def _show_tournament_data_frame(self):
        self._clear_frame()
        self.frame = tournament_frame.TournamentFrame(self, self.data_manager)
    
    def _show_player_data_frame(self):
        self._clear_frame()
        self.frame = player_frame.PlayerFrame(self, self.data_manager)

    def _show_ranking_rules_frame(self):
        pass
    
    def run(self):
        # Start the application
        self.mainloop()