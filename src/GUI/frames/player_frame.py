"""Player management GUI frames.

Contains the `PlayerFrame` landing frame and a collection of
internal frames used to add/remove/edit players and ranking types.
These frames are composed by the main application window and rely
on a `DataManager` instance for persistence.
"""

import tkinter as tk
import customtkinter as ctk
import GUI.window as window
from ranking.data_manager import DataManager
from GUI.utils import MultipleOptionsFrame, NumberEntry, CollapsibleFrame


class PlayerFrame(ctk.CTkFrame):
    """Top-level player management frame composed of three columns.

    Args:
        master: Parent widget (usually the root window).
        data_manager (DataManager): Provides access to players and rankings.
    """
    def __init__(self, master, data_manager: DataManager):
        super().__init__(master)

        # Main frame for the player frame
        self.pack(fill="both", expand=True)

        self.data_manager = data_manager
        # Add frame to the left with buttons
        self.left_frame = _LeftFrame(self)
        self.middle_frame = _DefaultMiddleFrame(self)
        self.right_frame = _RightFrame(self)
        
    def _show_default_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="disabled")
        self.middle_frame = _DefaultMiddleFrame(self)
        
    def _show_add_player_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _AddPlayerMiddleFrame(self)
    
    def _show_remove_player_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _RemovePlayerMiddleFrame(self)
        
    def _show_edit_player_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _EditPlayerMiddleFrame(self)
    
    def _show_add_ranking_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _AddRankingMiddleFrame(self)
        
    def _show_remove_ranking_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _RemoveRankingMiddleFrame(self)
        
    def _show_edit_ranking_middle_frame(self):
        self.middle_frame.destroy()
        self.left_frame.button7.configure(state="normal")
        self.middle_frame = _EditRankingMiddleFrame(self)
    
    def _reload_right_frame(self):
        self.right_frame.destroy()
        self.right_frame = _RightFrame(self)

class _LeftFrame(ctk.CTkFrame):
    """Left-side navigation and action buttons for player management."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="y")
        self.configure(width=300)

        # Add frame title
        self.title_label = ctk.CTkLabel(self, text="Options", font=ctk.CTkFont(size=25, weight="bold"), wraplength=200)
        self.title_label.pack(padx=15, pady=(15, 0))

        # Add player options title
        self.title_label_1 = ctk.CTkLabel(self, text="Player Options", font=ctk.CTkFont(size=16, weight="bold"), wraplength=200)
        self.title_label_1.pack(padx=5, pady=(0, 0))

        # Add buttons for navigation
        self.button1 = ctk.CTkButton(self, text="Add Player", command=master._show_add_player_middle_frame)
        self.button1.pack(padx=15, pady=(5, 10))

        self.button2 = ctk.CTkButton(self, text="Remove Player", command=master._show_remove_player_middle_frame)
        self.button2.pack(padx=15, pady=10)

        self.button3 = ctk.CTkButton(self, text="Edit Player", command=master._show_edit_player_middle_frame)
        self.button3.pack(padx=15, pady=10)

        self.title_label_2 = ctk.CTkLabel(self, text="Ranking Options", font=ctk.CTkFont(size=16, weight="bold"), wraplength=200)
        self.title_label_2.pack(padx=15, pady=(5, 0))

        self.button4 = ctk.CTkButton(self, text="Add Ranking", command=master._show_add_ranking_middle_frame)
        self.button4.pack(padx=15, pady=(5, 5))

        self.button5 = ctk.CTkButton(self, text="Remove Ranking", command=master._show_remove_ranking_middle_frame)
        self.button5.pack(padx=15, pady=10)

        self.button6 = ctk.CTkButton(self, text="Edit Ranking", command=master._show_edit_ranking_middle_frame)
        self.button6.pack(padx=15, pady=10)

        self.button7 = ctk.CTkButton(self, text="Go Back", command=master._show_default_middle_frame, state="disabled")
        self.button7.pack(padx=15, pady=10)

        self.button8 = ctk.CTkButton(self, text="Return to Main", command=master.master._show_home_frame)
        self.button8.pack(padx=15, pady=20, side="bottom")
        
class _DefaultMiddleFrame(ctk.CTkFrame):
    """Default center pane describing player management features."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Player Data", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add scrollable text box for tournament data display
        self.textbox = ctk.CTkTextbox(self, width=600, height=275, wrap="word")
        self.textbox.pack(pady=10)
        welcome_message = (
            "Here you can manage how some players are represented in the ranking calculations.\n\n"
            "Use the options on the left to add, remove or edit players and their rankings.\n\n"
            "When adding a player, you can specify their ranking.\n\n"
            "When adding or editing a ranking, you will be able to set a multiplier to adjust how much the ranking affects the player's total points.\n\n"
        )
        self.textbox.insert("0.0", welcome_message)
        self.textbox.configure(state="disabled")
        
class _RightFrame(ctk.CTkFrame):
    """Right-side info panel listing players and ranking columns."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="right", fill="y")
        self.configure(width=300)

        # Add frame title
        self.title_label = ctk.CTkLabel(self, text="Player Info", font=ctk.CTkFont(size=25, weight="bold"), wraplength=200)
        self.title_label.pack(padx=15, pady=10)

        # Add additional info widgets here
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        self.tabview.add("Players")
        self.tabview.add("Rankings")

        # Set players tab content
        players = master.data_manager.get_players()
        players_tab = self.tabview.tab("Players")
        if players:
            for player_name, ranking_data in players.items():
                player_info = {
                    "Rankings": ", ".join(ranking_data) if ranking_data else "None"
                }
                player_frame = CollapsibleFrame(players_tab, title=player_name, data=player_info, height=60)
                player_frame.pack(fill="x", pady=5)
        else:
            no_players_label = ctk.CTkLabel(players_tab, text="No players available.")
            no_players_label.pack(pady=10)

        # Set rankings tab content
        rankings = master.data_manager.get_rankings()
        rankings_tab = self.tabview.tab("Rankings")
        if rankings:
            for ranking_name, multiplier in rankings.items():
                ranking_info = {
                    "Multiplier": multiplier
                }
                ranking_frame = CollapsibleFrame(rankings_tab, title=ranking_name, data=ranking_info, height=30)
                ranking_frame.pack(fill="x", pady=5)
        
class _AddPlayerMiddleFrame(ctk.CTkFrame):
    """Middle pane for adding a new player and assigning rankings."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Add Player", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for adding a player here
        self.player_name_label = ctk.CTkLabel(self, text="Player Name:")
        self.player_name_label.pack(pady=5)
        self.player_name_entry = ctk.CTkEntry(self, width=300, placeholder_text="Enter player name")
        self.player_name_entry.pack(pady=5)

        # Add widget for adding a player to a ranking
        self.ranking_label = ctk.CTkLabel(self, text="Select Ranking:")
        self.ranking_label.pack(pady=5)
        self.ranking_optionmenu = MultipleOptionsFrame(
            self,
            title="Rankings",
            options=list(master.data_manager.get_rankings().keys()),
            height=150,
        )
        self.ranking_optionmenu.pack(pady=10)

        self.add_button = ctk.CTkButton(self, text="Add Player", command=self._add_player)
        self.add_button.pack(pady=20)

    def _add_player(self):
        """Collect input and add a new player via the DataManager."""
        player_name = self.player_name_entry.get()
        selected_rankings = self.ranking_optionmenu.get_selected_options()
        if player_name:
            self.master.data_manager.add_player(player_name, selected_rankings)
            self.player_name_entry.delete(0, 'end')
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_add_player_middle_frame()  # Refresh the middle frame

class _RemovePlayerMiddleFrame(ctk.CTkFrame):
    """Middle pane for selecting and removing an existing player."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Remove Player", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for removing a player here
        self.player_label = ctk.CTkLabel(self, text="Select Player to Remove:")
        self.player_label.pack(pady=5)
        self.player_optionmenu = ctk.CTkOptionMenu(
            self,
            values=[player for player in master.data_manager.get_players().keys()] if master.data_manager.get_players() else ["No Players"],
            variable=tk.StringVar(value=list(master.data_manager.get_players().keys())[0] if master.data_manager.get_players() else "No Players"),
        )
        self.player_optionmenu.pack(pady=5)

        self.remove_button = ctk.CTkButton(self, text="Remove Player", command=self._remove_player)
        self.remove_button.pack(pady=20)

    def _remove_player(self):
        """Remove the selected player via the DataManager."""
        selected_player = self.player_optionmenu.get()
        if selected_player:
            self.master.data_manager.remove_player(selected_player)
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_remove_player_middle_frame()  # Refresh the middle frame

class _EditPlayerMiddleFrame(ctk.CTkFrame):
    """Pane to edit a player's assigned rankings."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Edit Player", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for editing a player here
        self.player_label = ctk.CTkLabel(self, text="Select Player to Edit:")
        self.player_label.pack(pady=5)
        self.selected_player = tk.StringVar()
        if master.data_manager.get_players():
            self.selected_player.set(list(master.data_manager.get_players().keys())[0])
        else:
            self.selected_player.set("No Players")

        self.player_optionmenu = ctk.CTkOptionMenu(
            self,
            values=[player for player in master.data_manager.get_players().keys()] if master.data_manager.get_players() else ["No Players"],
            variable=self.selected_player,
            command=self._on_player_selected,
        )
        self.player_optionmenu.pack(pady=5)

        # Add widget to edit player rankings
        self.ranking_label = ctk.CTkLabel(self, text="Edit Player Rankings:")
        self.ranking_label.pack(pady=5)

        self.ranking_optionmenu = MultipleOptionsFrame(
            self,
            title="Rankings",
            options=list(master.data_manager.get_rankings().keys()),
        )

        self.edit_button = ctk.CTkButton(self, text="Edit Player", command=self._edit_player)
        self.edit_button.pack(pady=20)

    def _edit_player(self):
        """Apply ranking changes to the selected player and refresh UI."""
        selected_player = self.player_optionmenu.get()
        if selected_player:
            master.data_manager.edit_player(selected_player, self.ranking_optionmenu.get_selected_options())
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_edit_player_middle_frame()  # Refresh the middle frame
            pass

    def _on_player_selected(self, selected_player):
        """Populate ranking selections when a player is selected."""
        rankings = self.master.data_manager.get_player_rankings(selected_player)
        self.ranking_optionmenu.set_selected_options([])  # Clear previous selections
        self.ranking_optionmenu.set_selected_options(rankings)
        
class _AddRankingMiddleFrame(ctk.CTkFrame):
    """Pane for creating a new ranking column and multiplier."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Add Ranking", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for adding a ranking here
        self.ranking_name_label = ctk.CTkLabel(self, text="Ranking Name:")
        self.ranking_name_label.pack(pady=5)
        self.ranking_name_entry = ctk.CTkEntry(self, width=300, placeholder_text="Enter ranking name")
        self.ranking_name_entry.pack(pady=5)

        # Add widget for adding a ranking multiplier
        self.ranking_multiplier_label = ctk.CTkLabel(self, text="Ranking Multiplier:")
        self.ranking_multiplier_label.pack(pady=5)
        self.ranking_multiplier_entry = NumberEntry(self)
        self.ranking_multiplier_entry.pack(pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Ranking", command=self._add_ranking)
        self.add_button.pack(pady=20)

    def _add_ranking(self):
        """Create a new ranking using the DataManager and refresh UI."""
        ranking_name = self.ranking_name_entry.get()
        ranking_multiplier = self.ranking_multiplier_entry.get_value()
        if ranking_name:
            self.master.data_manager.add_ranking(ranking_name, ranking_multiplier)
            self.ranking_name_entry.delete(0, 'end')
            self.ranking_multiplier_entry.delete(0, 'end')
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_add_ranking_middle_frame()  # Refresh the middle frame

class _RemoveRankingMiddleFrame(ctk.CTkFrame):
    """Pane to remove an existing ranking column."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Remove Ranking", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for removing a ranking here
        self.ranking_label = ctk.CTkLabel(self, text="Select Ranking to Remove:")
        self.ranking_label.pack(pady=5)
        self.ranking_optionmenu = ctk.CTkOptionMenu(
            self,
            values=[ranking for ranking in master.data_manager.get_rankings().keys()],
            variable=tk.StringVar(value=list(master.data_manager.get_rankings().keys())[0]), # There's always at least one ranking
        )
        self.ranking_optionmenu.pack(pady=5)

        self.remove_button = ctk.CTkButton(self, text="Remove Ranking", command=self._remove_ranking)
        self.remove_button.pack(pady=20)

    def _remove_ranking(self):
        """Remove the selected ranking type and refresh UI."""
        selected_ranking = self.ranking_optionmenu.get()
        if selected_ranking and selected_ranking != "No Ranking":
            self.master.data_manager.remove_ranking(selected_ranking)
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_remove_ranking_middle_frame()  # Refresh the middle frame
            
class _EditRankingMiddleFrame(ctk.CTkFrame):
    """Pane to edit the multiplier of an existing ranking."""
    def __init__(self, master):
        super().__init__(master)

        self.pack(side="left", fill="both", expand=True)
        self.configure(fg_color="transparent", height=300)
        self.title_label = ctk.CTkLabel(self, text="Edit Ranking", font=ctk.CTkFont(size=25, weight="bold"))
        self.title_label.pack(pady=20)

        # Add widgets for editing a ranking here
        self.ranking_label = ctk.CTkLabel(self, text="Select Ranking to Edit:")
        self.ranking_label.pack(pady=5)
        self.ranking_optionmenu = ctk.CTkOptionMenu(
            self,
            values=[ranking for ranking in master.data_manager.get_rankings().keys()],
            variable=tk.StringVar(value=list(master.data_manager.get_rankings().keys())[0]), # There's always at least one ranking
        )
        self.ranking_optionmenu.pack(pady=5)

        # Add widget for editing a ranking multiplier
        self.ranking_multiplier_label = ctk.CTkLabel(self, text="New Ranking Multiplier:")
        self.ranking_multiplier_label.pack(pady=5)
        self.ranking_multiplier_entry = NumberEntry(self)
        self.ranking_multiplier_entry.pack(pady=5)

        self.edit_button = ctk.CTkButton(self, text="Edit Ranking", command=self._edit_ranking)
        self.edit_button.pack(pady=20)

    def _edit_ranking(self):
        """Set a new multiplier for the selected ranking and refresh UI."""
        selected_ranking = self.ranking_optionmenu.get()
        new_multiplier = self.ranking_multiplier_entry.get_value()
        if selected_ranking and new_multiplier:
            self.master.data_manager.edit_ranking(selected_ranking, float(new_multiplier))
            self.ranking_multiplier_entry.delete(0, 'end')
            # Optionally, show a success message or update the UI accordingly
            self.master._reload_right_frame()
            self.master._show_edit_ranking_middle_frame()  # Refresh the middle frame



