from tkinter import *
import customtkinter as ctk

class CollapsibleFrame(ctk.CTkFrame):
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
            hover_color=("gray80","gray30")
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
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.header.configure(text=f"▶ {self.title}")
        else:
            self.content_frame.pack(fill="x", pady=5)
            self.header.configure(text=f"▼ {self.title}")
        self.is_expanded = not self.is_expanded

class MultipleOptionsFrame(ctk.CTkFrame):
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
            hover_color=("gray80","gray30")
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
        if self.is_expanded:
            self.content_frame.pack_forget()
            self.header.configure(text=f"▶ {self.title}")
        else:
            self.content_frame.pack(fill="x", pady=5)
            self.header.configure(text=f"▼ {self.title}")
        self.is_expanded = not self.is_expanded        
            
    def get_selected_options(self):
        return [v for v, var in self.option_vars.items() if var.get()]
    
    def set_selected_options(self, selected_options):
        for option, var in self.option_vars.items():
            var.set(option in selected_options)

class NumberEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Register validation command
        vcmd = (self.register(self._validate_input), '%P')
        self.configure(validate="key", validatecommand=vcmd)
        
    def _validate_input(self, proposed_value):
        # Allow only digits and empty string
        return proposed_value.isdigit() or proposed_value == ""

    def get_value(self):
        value = self.get()
        return int(value) if value.isdigit() else None
        