"""Tournament management frames for the GUI.

Provides `TournamentFrame` (top-level) and internal frames used to
add, remove and edit tournaments. Frames rely on a `DataManager`
instance for persistence and use small GUI utilities from
`GUI.utils` for compact displays.
"""

import tkinter as tk
import customtkinter as ctk
import GUI.window as window
from ranking.data_manager import DataManager
import GUI.utils as gui_utils


class TournamentFrame(ctk.CTkFrame):
    """Top-level tournament management frame composed of three columns.

    Args:
        master: Parent widget (usually the root window).
        data_manager (DataManager): Provides access to tournaments and tiers.
    """
    def __init__(self, master, data_manager: DataManager):
        super().__init__(master)

        # Main frame for the tournament frame
        self.pack(fill="both", expand=True)

        self.data_manager = data_manager
        # Add frame to the left with buttons
        self.left_frame = _LeftFrame(self)
        self.middle_frame = _DefaultMiddleFrame(self)
        self.right_frame = _RightFrame(self)

    def _show_default_middle_frame(self):
        """Restore the default middle pane and disable the back button."""
        self.middle_frame.destroy()
        self.left_frame.button4.configure(state="disabled")
        self.middle_frame = _DefaultMiddleFrame(self)

    def _show_add_tournament_middle_frame(self):
        """Switch to the Add Tournament pane."""
        self.middle_frame.destroy()
        self.left_frame.button4.configure(state="normal")
        self.middle_frame = _AddTournamentMiddleFrame(self)

    def _show_remove_tournament_middle_frame(self):
        """Switch to the Remove Tournament pane."""
        self.middle_frame.destroy()
        self.left_frame.button4.configure(state="normal")
        self.middle_frame = _RemoveTournamentMiddleFrame(self)

    def _show_edit_tournament_middle_frame(self):
        """Switch to the Edit Tournament pane."""
        self.middle_frame.destroy()
        self.left_frame.button4.configure(state="normal")
        self.middle_frame = _EditTournamentMiddleFrame(self)

    def _reload_right_frame(self):
        """Recreate the right-side summary frame to reflect updates."""
        self.right_frame.destroy()
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
        
        # Add additional widgets for tournament data here
        self.button1 = ctk.CTkButton(self, text="Add Tournament", command=master._show_add_tournament_middle_frame)
        self.button1.pack(padx=15, pady=10)
        
        self.button2 = ctk.CTkButton(self, text="Remove Tournament", command=master._show_remove_tournament_middle_frame)
        self.button2.pack(padx=15, pady=10)
        
        self.button3 = ctk.CTkButton(self, text="Edit Tournament", command=master._show_edit_tournament_middle_frame)
        self.button3.pack(padx=15, pady=10)
        
        self.button4 = ctk.CTkButton(self, text="Go Back", command=master._show_default_middle_frame, state="disabled")
        self.button4.pack(padx=15, pady=10)
        
        self.button5 = ctk.CTkButton(self, text="Return to Main", command=master.master._show_home_frame)
        self.button5.pack(side="bottom", padx=15, pady=20)
        
class _RightFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="right", fill="y")
        self.configure(width=300)
        
        # Add frame title
        self.title_label = ctk.CTkLabel(self, text="Tournament Data", font=ctk.CTkFont(size=25, weight="bold"), wraplength=200)
        self.title_label.pack(padx=15, pady=10)
        
        # Scrollable frame with tournament data
        self.data_frame = ctk.CTkScrollableFrame(self)
        self.data_frame.pack(padx=5, fill="both", expand=True)
        
        # Populate with tournament data
        for tournament in master.data_manager.get_tournaments():
            tournament_info = {
                "Entrants": tournament['entrants'],
                "Tier": tournament['tier'],
                "Link": tournament['link']
            }
            tournament_frame = gui_utils.CollapsibleFrame(self.data_frame, title=tournament['name'], data=tournament_info, height=60)
            tournament_frame.pack(fill="x", padx=5)
    
class _DefaultMiddleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="both", expand=True)
        master.left_frame.button4.configure(state="disabled")
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Tournament Data", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Add scrollable text box for tournament data display
        self.textbox = ctk.CTkTextbox(self, width=600, height=275, wrap="word")
        self.textbox.pack(pady=10)
        welcome_message = (
            "Here you can manage which tournaments are included in the ranking calculations.\n"
            "Use the options on the left to add, remove, or edit tournament data.\n\n"
            "To add a tournament, click 'Add Tournament' and add the tournament details.\n"
            "This includes the tournament link (currently only StartGG links are supported), and the tier of the tournament.\n"
            "By default, only tiers from SS to D are supported, but you can add/remove tiers in the 'Ranking Rules' section.\n\n"
            "To remove a tournament, click 'Remove Tournament' and select the tournament you wish to delete from the ranking calculations.\n\n"
            "To edit a tournament, click 'Edit Tournament' and select the tournament you wish to modify.\n"
            "You can change the tier of the tournament or add special rules if necessary (e.g, specific location, etc).\n"
            "You can check the tournament details by clicking on the tournament links provided in the right frame. \n"                    
        )
        self.textbox.insert("0.0", welcome_message)
        self.textbox.configure(state="disabled")

class _AddTournamentMiddleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=400)
        self.title_label = ctk.CTkLabel(self, text="Add Tournament", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Add widgets for adding tournament details here
        self.link_label = ctk.CTkLabel(self, text="Tournament Link:")
        self.link_label.pack(pady=10)
        self.link_entry = ctk.CTkEntry(self, width=400, placeholder_text="start.gg/tournament/your-tournament/event/your-event")
        self.link_entry.pack(pady=10)
        
        self.tier_label = ctk.CTkLabel(self, text="Tournament Tier:")
        self.tier_label.pack(pady=10)
        self.tier_entry = ctk.CTkOptionMenu(self, values=["SS", "S", "A", "B", "C", "D"], variable = ctk.StringVar(value="D"))
        self.tier_entry.pack(pady=10)
        
        self.add_button = ctk.CTkButton(self, text="Submit", command=self._submit_tournament)
        self.add_button.pack(pady=20)
        
    def _submit_tournament(self):
        link = self.link_entry.get()
        tier = self.tier_entry.get()
        self.master.data_manager.add_tournament(link, tier)
        self.link_entry.delete(0, 'end')
        self.master._reload_right_frame()
        # Show confirmation message or error message on logger (to be implemented)
        
class _RemoveTournamentMiddleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="both", expand=True)
        master.left_frame.button4.configure(state="normal")
        self.configure(fg_color="transparent", height=400)
        self.title_label = ctk.CTkLabel(self, text="Remove Tournament", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Add widgets for removing tournament details here
        self.info_label = ctk.CTkLabel(self, text="Select the tournament you wish to remove from the ranking calculations.")
        self.info_label.pack(pady=10)
        
        self.tournament_optionmenu = ctk.CTkOptionMenu(
            self, 
            values=[t['name'] for t in master.data_manager.get_tournaments()] if master.data_manager.get_tournaments() else ["No Tournaments"], 
            variable = ctk.StringVar(value=master.data_manager.get_tournaments()[0]['name'] if master.data_manager.get_tournaments() else "No Tournaments")
            )
        self.tournament_optionmenu.pack(pady=10)
        
        self.remove_button = ctk.CTkButton(self, text="Remove", command=self._remove_tournament)
        self.remove_button.pack(pady=20)
        
    def _remove_tournament(self):
        tournament_name = self.tournament_optionmenu.get()
        self.master.data_manager.remove_tournament(tournament_name)
        self.master._reload_right_frame()
        self.master._show_remove_tournament_middle_frame()  # Refresh the middle frame
        # Show confirmation message or error message on logger (to be implemented)
        
class _EditTournamentMiddleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.pack(side="left", fill="both", expand=True)
        master.left_frame.button4.configure(state="normal")
        self.configure(fg_color="transparent", height=400)
        self.title_label = ctk.CTkLabel(self, text="Edit Tournament", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Add widgets for editing tournament details here
        self.info_label = ctk.CTkLabel(self, text="Select the tournament you wish to edit.")
        self.info_label.pack(pady=10)
        
        self.tournament_optionmenu = ctk.CTkOptionMenu(
            self, 
            values=[t['name'] for t in master.data_manager.get_tournaments()] if master.data_manager.get_tournaments() else ["No Tournaments"], 
            variable = ctk.StringVar(value=master.data_manager.get_tournaments()[0]['name'] if master.data_manager.get_tournaments() else "No Tournaments")
            )
        self.tournament_optionmenu.pack(pady=10)
        
        self.info_label2 = ctk.CTkLabel(self, text= "Edit the tournament tier:")
        self.info_label2.pack(pady=10)
        
        self.tier_entry = ctk.CTkOptionMenu(
            self, 
            values=["SS", "S", "A", "B", "C", "D"], 
            variable = ctk.StringVar(value=master.data_manager.get_tournaments()[0]['tier'] if master.data_manager.get_tournaments() else "D")
            )
        self.tier_entry.pack(pady=10)
        
        self.edit_button = ctk.CTkButton(self, text="Edit", command=self._edit_tournament)
        self.edit_button.pack(pady=20)
        
    def _edit_tournament(self):
        tournament_name = self.tournament_optionmenu.get()
        new_tier = self.tier_entry.get()
        
        self.master.data_manager.change_tournament_tier(tournament_name, new_tier)
        self.master._reload_right_frame()
        self.master._show_edit_tournament_middle_frame()  # Refresh the middle frame
        # Logic to edit the selected tournament (to be implemented)