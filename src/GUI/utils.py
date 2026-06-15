"""Small reusable GUI widgets used across the app.

Contains lightweight helper frames and entry widgets used by the
application frames. The widgets are implemented using `customtkinter`.
"""

from tkinter import *
import customtkinter as ctk


class CollapsibleFrame(ctk.CTkFrame):
    """A frame with a clickable header that expands/collapses content.

    Args (via kwargs):
        title (str): Header text.
        data (dict): Key/value pairs to display inside the content box.
        height (int): Optional textbox height.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master)

        self.is_expanded = False
        self.title = kwargs.get("title", "")
        self.data = kwargs.get("data", {})

        # Header button
        self.header = ctk.CTkButton(
            self,
            text=f"▶ {self.title}",
            anchor="w",
            command=self._toggle,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
        )
        self.header.pack(fill="x")

        # Content frame (initially hidden)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="x")
        self.content_frame.pack_forget()

        # Populate content
        info = "\n".join(f"{key}: {value}" for key, value in self.data.items())

        self.textbox = ctk.CTkTextbox(
            self.content_frame,
            wrap="word",
            height=kwargs.get("height", 80),
        )
        self.textbox.insert("1.0", info)
        self.textbox.configure(state="disabled")
        self.textbox.pack(fill="x")

    def _toggle(self):
        """Toggle visibility of the content area."""
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.header.configure(text=f"▶ {self.title}")
        else:
            self.content_frame.pack(fill="x", pady=5)
            self.header.configure(text=f"▼ {self.title}")
        self.is_expanded = not self.is_expanded


class MultipleOptionsFrame(ctk.CTkFrame):
    """A collapsible frame containing multiple checkbox options.

    Args (via kwargs):
        title (str): Header text.
        options (list[str]): Option labels to render as checkboxes.
        expanded (bool): Whether the content should start expanded.
        height (int): Height for the content area.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master)

        # Main button to expand/collapse
        self.is_expanded = kwargs.get("expanded", False)
        self.title = kwargs.get("title", "Options")
        self.options = kwargs.get("options", [])
        self.height = kwargs.get("height", 100)
        print(self.options)
        self.option_vars = {v: ctk.BooleanVar(value=False) for v in self.options}

        self.header = ctk.CTkButton(
            self,
            text=f"▶ {self.title}",
            anchor="w",
            command=self._toggle,
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
        )
        self.header.pack(fill="x", pady=5)

        self.content_frame = ctk.CTkFrame(self, height=self.height)
        self.content_frame.pack(fill="x")
        self.content_frame.propagate(False)
        self.content_frame.pack_forget()

        # Menu with checkboxes (initially hidden)
        self.menu_frame = ctk.CTkScrollableFrame(self.content_frame)
        self.menu_frame.pack(fill="x", pady=5)

        for option, var in self.option_vars.items():
            checkbox = ctk.CTkCheckBox(
                self.menu_frame,
                text=option,
                variable=var,
            )
            checkbox.pack(anchor="w", padx=5, pady=2)

    def _toggle(self):
        """Toggle visibility of the menu content."""
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.header.configure(text=f"▶ {self.title}")
        else:
            self.content_frame.pack(fill="x", pady=5)
            self.header.configure(text=f"▼ {self.title}")
        self.is_expanded = not self.is_expanded

    def get_selected_options(self):
        """Return a list of selected option labels."""
        return [v for v, var in self.option_vars.items() if var.get()]

    def set_selected_options(self, selected_options):
        """Mark the provided options as selected.

        Args:
            selected_options (list[str]): Options to mark as selected.
        """
        for option, var in self.option_vars.items():
            var.set(option in selected_options)


class NumberEntry(ctk.CTkEntry):
    """An entry widget that allows only numeric input.

    Methods:
        get_value(): return int value or None when empty/invalid.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Register validation command
        vcmd = (self.register(self._validate_input), '%P')
        self.configure(validate="key", validatecommand=vcmd)

    def _validate_input(self, proposed_value):
        """Validation callback for the entry (digits or empty)."""
        return proposed_value.isdigit() or proposed_value == ""

    def get_value(self):
        """Return the integer value or None if not set."""
        value = self.get()
        return int(value) if value.isdigit() else None
        