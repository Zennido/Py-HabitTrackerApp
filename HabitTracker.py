import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import pandas as pd
import os

class HabitTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Habit Tracker")
        self.geometry("500x600")

        # Habit data storage (starts empty)
        self.habits = {}

        # Set up the UI
        self.create_widgets()

        # Load habits from CSV if the file exists
        self.load_habits_from_csv()

    def create_widgets(self):
        # Title label
        self.label_title = ctk.CTkLabel(self, text="Habit Tracker", font=("Arial", 24))
        self.label_title.pack(pady=10)

        # Habit list UI (Initially empty, updated dynamically)
        self.frame_habits = ctk.CTkFrame(self)
        self.frame_habits.pack(pady=20)

        # Add habit section
        self.entry_habit_name = ctk.CTkEntry(self, placeholder_text="Habit Name")
        self.entry_habit_name.pack(pady=10)
        
        self.entry_habit_goal = ctk.CTkEntry(self, placeholder_text="Habit Goal (e.g. 30 min, 8 glasses)")
        self.entry_habit_goal.pack(pady=10)

        self.btn_add_habit = ctk.CTkButton(self, text="Add Habit", command=self.add_habit)
        self.btn_add_habit.pack(pady=10)

        # AI recommendations area
        self.label_recommendation = ctk.CTkLabel(self, text="AI Recommendations:", font=("Arial", 16))
        self.label_recommendation.pack(pady=10)
        
        # Increased the size of the AI recommendations textbox
        self.recommendation_text = ctk.CTkTextbox(self, height=150, width=350)  # Increased size
        self.recommendation_text.pack(pady=10)
        
        # Button to generate recommendations
        self.btn_recommend = ctk.CTkButton(self, text="Generate Recommendations", command=self.generate_recommendations)
        self.btn_recommend.pack(pady=10)

    def add_habit(self):
        habit_name = self.entry_habit_name.get().strip()
        habit_goal = self.entry_habit_goal.get().strip()

        if habit_name and habit_goal:
            # Add new habit to the dictionary
            if habit_name not in self.habits:
                self.habits[habit_name] = {
                    'goal': habit_goal,
                    'current': 0,
                    'last_checked': None
                }
                # Add a new button for the habit
                self.create_habit_button(habit_name, habit_goal)
                # Clear input fields
                self.entry_habit_name.delete(0, tk.END)
                self.entry_habit_goal.delete(0, tk.END)
                
                # Save habits to CSV after adding
                self.save_habits_to_csv()
            else:
                self.show_warning("Habit already exists!")
        else:
            self.show_warning("Please provide a valid habit name and goal.")

    def create_habit_button(self, habit_name, habit_goal):
        """ Create a button for the new habit with an additional 'Goal Achieved' button. """
        button_frame = ctk.CTkFrame(self.frame_habits)
        button_frame.pack(pady=5, fill=tk.X)

        habit_button = ctk.CTkButton(button_frame, text=f"{habit_name} (Goal: {habit_goal})",
                                      command=lambda habit=habit_name: self.update_habit(habit))
        habit_button.pack(side=tk.LEFT, padx=5)

        goal_button = ctk.CTkButton(button_frame, text="Goal Achieved", 
                                     command=lambda habit=habit_name: self.mark_goal_achieved(habit))
        goal_button.pack(side=tk.LEFT, padx=5)

    def update_habit(self, habit):
        """ Increment the habit count and update the time. """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.habits[habit]['current'] += 1
        self.habits[habit]['last_checked'] = current_time
        
        # After updating the habit, refresh recommendations
        self.generate_recommendations()
        
        # Save habits to CSV after updating
        self.save_habits_to_csv()

    def mark_goal_achieved(self, habit):
        """ Mark the habit as completed by setting the current progress to the goal. """
        goal = int(self.habits[habit]['goal'])
        self.habits[habit]['current'] = goal
        self.habits[habit]['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # After marking the goal, refresh recommendations
        self.generate_recommendations()
        
        # Save habits to CSV after marking goal as achieved
        self.save_habits_to_csv()

    def generate_recommendations(self):
        """ Generate AI recommendations based on habit progress. """
        recommendations = []

        for habit, data in self.habits.items():
            goal = int(data['goal'])
            current = data['current']
            
            if current < goal:
                remaining = goal - current
                recommendations.append(f"Focus on '{habit}'! You need {remaining} more units to reach your goal.")
            else:
                recommendations.append(f"Great job on '{habit}'! You've reached your goal.")
        
        # Display the recommendations
        self.recommendation_text.delete(1.0, tk.END)
        self.recommendation_text.insert(tk.END, "\n".join(recommendations))

    def save_habits_to_csv(self):
        """ Save the habits to a CSV file using pandas. """
        # Convert the habits dictionary to a pandas DataFrame
        habit_data = {
            'habit_name': [],
            'goal': [],
            'current': [],
            'last_checked': []
        }
        
        for habit, data in self.habits.items():
            habit_data['habit_name'].append(habit)
            habit_data['goal'].append(data['goal'])
            habit_data['current'].append(data['current'])
            habit_data['last_checked'].append(data['last_checked'])
        
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(habit_data)

        # Save DataFrame to a CSV file
        df.to_csv("habits.csv", index=False)

    def load_habits_from_csv(self):
        """ Load habits from a CSV file if it exists. """
        if os.path.exists("habits.csv"):
            df = pd.read_csv("habits.csv")
            for index, row in df.iterrows():
                habit_name = row['habit_name']
                habit_goal = row['goal']
                habit_current = row['current']
                habit_last_checked = row['last_checked']
                self.habits[habit_name] = {
                    'goal': habit_goal,
                    'current': habit_current,
                    'last_checked': habit_last_checked if pd.notna(habit_last_checked) else None
                }
                # Re-create buttons for existing habits
                self.create_habit_button(habit_name, habit_goal)

    def show_warning(self, message):
        """ Display a simple warning message. """
        warning_popup = ctk.CTkToplevel(self)
        warning_popup.title("Warning")
        label = ctk.CTkLabel(warning_popup, text=message, fg_color="red", font=("Arial", 16))
        label.pack(pady=20)
        btn_close = ctk.CTkButton(warning_popup, text="Close", command=warning_popup.destroy)
        btn_close.pack(pady=10)

# Run the application
if __name__ == "__main__":
    app = HabitTrackerApp()
    app.mainloop()
