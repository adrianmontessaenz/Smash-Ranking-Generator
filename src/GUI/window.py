"""GUI application window for the Ranking Generator.

This module defines `AppWindow`, the top-level application window
built on `customtkinter`. It composes the different frames (home,
tournament, player) and exposes a `run()` method to start the GUI.
"""

from tkinter import *
import customtkinter
import GUI.frames.home_frame as home_frame
import GUI.frames.tournament_frame as tournament_frame
import GUI.frames.player_frame as player_frame
from ranking.data_manager import DataManager


class AppWindow(customtkinter.CTk):
    """Main application window that switches between frames.

    The class accepts a `DataManager` instance which is passed down
    to child frames. Methods beginning with an underscore are
    internal helpers used to change the visible frame.
    """
    def __init__(self, data_manager: DataManager):
        """Create the application window and show the home frame.

        Args:
            data_manager (DataManager): Source of application data.
        """
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
        """Remove all child widgets from the root window."""
        for widget in self.winfo_children():
            widget.destroy()

    def _show_home_frame(self):
        """Replace current content with the `HomeFrame`."""
        self._clear_frame()
        self.frame = home_frame.HomeFrame(self, self.data_manager)

    def _show_tournament_data_frame(self):
        """Replace current content with the `TournamentFrame`."""
        self._clear_frame()
        self.frame = tournament_frame.TournamentFrame(self, self.data_manager)

    def _show_player_data_frame(self):
        """Replace current content with the `PlayerFrame`."""
        self._clear_frame()
        self.frame = player_frame.PlayerFrame(self, self.data_manager)

    def _show_ranking_rules_frame(self):
        """Placeholder for showing ranking rules frame (not implemented)."""
        pass

    def run(self):
        """Start the GUI event loop."""
        self.mainloop()