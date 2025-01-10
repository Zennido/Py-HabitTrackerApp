import streamlit as st
import pandas as pd
import random
from sklearn.linear_model import LinearRegression

# File to store habits
csv_file = 'habits.csv'

# Motivational responses dictionary based on category
motivational_responses = {
    "Sports": [
        "You’re getting stronger every day, keep it up!",
        "Push yourself, because no one else is going to do it for you!",
        "The harder you work, the better you get!",
        "Champions keep playing until they get it right!",
        "Believe in yourself and all that you are!"
    ],
    "Study": [
        "Success is the sum of small efforts, repeated day in and day out!",
        "Don’t watch the clock; do what it does. Keep going!",
        "You’re one step closer to your goal. Stay focused!",
        "Hard work beats talent when talent doesn’t work hard!",
        "Success doesn’t come from what you do occasionally, it comes from what you do consistently!"
    ],
    "Work": [
        "The only way to do great work is to love what you do!",
        "Your hard work will pay off. Keep pushing!",
        "Don't stop when you're tired, stop when you're done!",
        "Strive for progress, not perfection!",
        "Success doesn’t come from what you do occasionally, it comes from what you do consistently!"
    ],
    "Home": [
        "Small progress is still progress. Keep going!",
        "A clean home is a happy home. Stay on track!",
        "Remember, every small step counts towards a bigger goal!",
        "Consistency is key to creating your ideal environment!",
        "Don’t rush, just focus and do it one step at a time!"
    ],
    "Hobby": [
        "Enjoy the process, not just the result!",
        "You’re doing amazing, keep fueling your passion!",
        "Every minute spent doing something you love is never wasted!",
        "Don’t stop doing what you love. It’s what makes life beautiful!",
        "Let your passion drive you, and the rest will follow!"
    ],
    "Other": [
        "Every small step forward counts. Keep going!",
        "You got this! Stay focused and keep working towards your goals!",
        "One day at a time. Progress is progress!",
        "Don't let obstacles stop you. Keep pushing forward!",
        "Believe in the process and trust that you'll reach your goal!"
    ]
}

# Load habits from CSV with error handling for empty file
def load_habits():
    try:
        return pd.read_csv(csv_file)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Habit', 'Category', 'Goal (hours)', 'Completed'])

# Save habits to CSV
def save_habits(df):
    df.to_csv(csv_file, index=False)

# Add a new habit with goal (hours)
def add_habit(habit, category, goal):
    df = load_habits()
    new_habit = pd.DataFrame({'Habit': [habit], 'Category': [category], 'Goal (hours)': [goal], 'Completed': [False]})
    df = pd.concat([df, new_habit], ignore_index=True)
    save_habits(df)

# Mark habit as complete
def mark_complete(habit):
    df = load_habits()
    df.loc[df['Habit'] == habit, 'Completed'] = True
    save_habits(df)

# Delete a habit
def delete_habit(habit):
    df = load_habits()
    df = df[df['Habit'] != habit]  # Remove the habit from the DataFrame
    save_habits(df)

# Get motivational responses based on category
def get_motivational_response(category):
    if category in motivational_responses:
        return random.choice(motivational_responses[category])
    else:
        return "Stay strong, you're doing great!"

# Predict the goal for a habit based on previous data (Linear Regression)
def predict_goal_for_habit(habit_category):
    df = load_habits()

    if df.empty:
        return 1.0  # Default goal if no data available

    # Convert categories to numerical format
    category_mapping = {cat: idx for idx, cat in enumerate(df['Category'].unique())}
    df['Category_num'] = df['Category'].map(category_mapping)

    X = df[['Category_num']]  # Category as feature
    y = df['Goal (hours)']  # Goal as target

    # Train the Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the goal for the given category
    habit_category_num = category_mapping.get(habit_category, -1)
    if habit_category_num == -1:
        return 1.0  # Default if category is not found

    predicted_goal = model.predict([[habit_category_num]])
    return predicted_goal[0]

# Load the habits at the beginning so that it is available for both pages and sidebar
df = load_habits()

# Navigation in sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Habit Tracker", "View Habits"])

# Habit categories
categories = ['Home', 'Sports', 'Study', 'Work', 'Hobby', 'Other']

if page == "Habit Tracker":
    # Input section for adding a new habit with goal prediction
    st.title("Habit Tracker")
    st.header("Add a New Habit")
    habit_name = st.text_input("Habit Name")
    habit_category = st.selectbox("Habit Category", categories)
    
    if habit_category:
        # Predict a goal for the selected category
        predicted_goal = predict_goal_for_habit(habit_category)
        st.write(f"Suggested Goal: {predicted_goal:.2f} hours")
    
    habit_goal = st.number_input("Goal (hours)", min_value=0.0, step=0.5, value=predicted_goal)
    
    if st.button("Add Habit"):
        if habit_name and habit_goal > 0:
            add_habit(habit_name, habit_category, habit_goal)
            st.success(f'Habit "{habit_name}" added to category "{habit_category}" with a goal of {habit_goal} hours.')
        else:
            st.error("Please enter a valid habit name and goal (hours).")

elif page == "View Habits":
    # Page to view and mark habits as complete and delete
    st.title("View Your Habits")
    
    if not df.empty:
        for index, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
            col1.write(f"{row['Habit']} ({row['Category']}) - Goal: {row['Goal (hours)']} hours")
            if col2.button("Mark as Complete", key=f"complete_{index}"):
                mark_complete(row['Habit'])
                st.rerun()  # Refresh the page after marking complete
            if row['Completed']:
                col3.write("✅ Completed")
            else:
                col3.write("❌ Not Completed")
            if col4.button("Delete", key=f"delete_{index}"):
                delete_habit(row['Habit'])
                st.rerun()  # Refresh the page after deletion
    else:
        st.write("No habits added yet.")

# Section for motivational response in the sidebar
st.sidebar.header("Need Motivation?")
if not df.empty:
    habit_for_motivation = st.sidebar.selectbox("Select a habit for motivation", df['Habit'].values)
    if st.sidebar.button("Get Motivation"):
        category = df.loc[df['Habit'] == habit_for_motivation, 'Category'].values[0]
        response = get_motivational_response(category)
        st.sidebar.info(response)
else:
    st.sidebar.warning("Please add some habits first.")
