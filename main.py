import json
import tkinter as tk


# Load tasks from a JSON file
def loadTasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
        return tasks
    except FileNotFoundError:
        return []


# Add a new task to the list
def add_task():
    task_name = entry.get()  # get whatever the user typed
    print(f"Button clicked! Task entered: {task_name}")
    entry.delete(0, tk.END)  # clear the entry box after adding


# Main logic
def main():
    tasks = loadTasks()
    # Debug, print all tasks
    for task in tasks:
        print(f"Task: {task['name']}, Due: {task['due_date']}, Priority: {task['priority']}")

    # Setup the UI
    global entry
    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("400x300")

    entry = tk.Entry(window, width=30)
    entry.pack(pady=10)

    add_button = tk.Button(window, text="Add Task", command=add_task)
    add_button.pack()

    window.mainloop()

if __name__ == "__main__":
    main()