import GUI.window as window
from GUI.ranking.data_manager import DataManager

if __name__ == "__main__":
    # Initialize and run the application
    data_manager = DataManager()
    app = window.AppWindow(data_manager)
    app.run()