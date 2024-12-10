import pandas as pd
import os
import heapq

# File to store habits
FILENAME = "habits.csv"

# Load habits from CSV file (if exists) or create a new DataFrame
def load_habits():
    if os.path.exists(FILENAME):
        return pd.read_csv(FILENAME)
    else:
        # Create a new DataFrame if the file doesn't exist
        return pd.DataFrame(columns=["Habit", "Goal", "Progress", "EstimatedEffort"])

# Save habits to CSV file
def save_habits(df):
    df.to_csv(FILENAME, index=False)

# Habit class for use in A* search
class Habit:
    def __init__(self, name, goal, progress, estimated_effort):
        self.name = name
        self.goal = goal
        self.progress = progress
        self.estimated_effort = estimated_effort  # Heuristic
    
    def is_complete(self):
        return self.progress >= self.goal
    
    def remaining_effort(self):
        return self.goal - self.progress
    
    def __lt__(self, other):
        # Comparison based on the cost (progress + heuristic)
        return (self.progress + self.estimated_effort) < (other.progress + other.estimated_effort)

# A* search algorithm to optimize habit completion
def a_star_search(habits):
    # Priority queue to explore habits with lowest cost + heuristic first
    frontier = []
    for habit in habits:
        heapq.heappush(frontier, habit)
    
    while frontier:
        current_habit = heapq.heappop(frontier)
        
        if current_habit.is_complete():
            print(f"Habit '{current_habit.name}' completed!")
            continue
        
        # Perform progress update (e.g., add effort or time)
        progress_increase = int(input(f"How much progress for {current_habit.name}? "))
        current_habit.progress += progress_increase
        print(f"Updated progress for {current_habit.name}: {current_habit.progress}/{current_habit.goal}")
        
        # Re-evaluate and add back to the frontier if not complete
        if not current_habit.is_complete():
            heapq.heappush(frontier, current_habit)

# Convert a DataFrame row into a Habit object
def df_to_habits(df):
    habits = []
    for _, row in df.iterrows():
        habits.append(Habit(row["Habit"], row["Goal"], row["Progress"], row["EstimatedEffort"]))
    return habits

# Add a new habit
def add_habit(df):
    habit_name = input("Enter the name of the habit: ")
    goal = int(input(f"Enter the goal for {habit_name} (e.g., number of times per week): "))
    estimated_effort = int(input(f"Estimate the effort needed to complete {habit_name} (e.g., difficulty level from 1-10): "))
    progress = 0  # Start with zero progress
    new_habit = pd.DataFrame({"Habit": [habit_name], "Goal": [goal], "Progress": [progress], "EstimatedEffort": [estimated_effort]})
    df = pd.concat([df, new_habit], ignore_index=True)
    save_habits(df)
    print(f"Habit '{habit_name}' added with a goal of {goal} and estimated effort of {estimated_effort}.")
    return df

# View all habits
def view_habits(df):
    if df.empty:
        print("No habits found. Add a new habit to get started.")
    else:
        print(df)

# Mark progress for a habit
def update_progress(df):
    habit_name = input("Enter the name of the habit to update progress: ")
    if habit_name in df['Habit'].values:
        progress_increase = int(input(f"How much progress do you want to add to '{habit_name}'? "))
        df.loc[df['Habit'] == habit_name, 'Progress'] += progress_increase
        save_habits(df)
        print(f"Progress updated for '{habit_name}'.")
    else:
        print(f"Habit '{habit_name}' not found.")
    return df

# Main menu
def menu():
    df = load_habits()
    while True:
        print("\n--- Habit Tracker ---")
        print("1. View habits")
        print("2. Add a new habit")
        print("3. Update progress")
        print("4. Optimize habits using A* search")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            view_habits(df)
        elif choice == '2':
            df = add_habit(df)
        elif choice == '3':
            df = update_progress(df)
        elif choice == '4':
            # Run A* search on habits
            habits = df_to_habits(df)
            a_star_search(habits)
        elif choice == '5':
            print("Exiting the habit tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the habit tracker
if __name__ == "__main__":
    menu()
