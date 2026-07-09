import json
import tkinter as tk


# Load tasks from a JSON file
def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
        return tasks
    except FileNotFoundError:
        return []


# Update the JSON file with the new task
def update_tasks(task_name):
    tasks = load_tasks()
    tasks.append({"name": task_name, "due_date": "", "priority": ""})
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent = 4)


# Add a new task to the list
def add_task():
    task_name = entry.get()

    # Avoid empty tasks
    if task_name.strip() == "":
        return
    
    entry.delete(0, tk.END)
    update_tasks(task_name)
    task_listbox.insert(tk.END, task_name)



# Clear all tasks from the list and the JSON file
def clear_tasks():
    task_listbox.delete(0, tk.END)
    with open("tasks.json", "w") as file:
        json.dump([], file, indent = 4)

# Main logic
def main():
    tasks = load_tasks()

    # Setup the UI
    global entry, task_listbox
    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("400x300")

    entry = tk.Entry(window, width=30)
    entry.pack(pady=10)

    add_button = tk.Button(window, text="Add Task", command=add_task)
    add_button.pack()

    clear_button = tk.Button(window, text="Clear Tasks", command=clear_tasks)
    clear_button.pack(pady=5)

    task_listbox = tk.Listbox(window, width=40, height=10)
    task_listbox.pack(pady=10)

    # Populate the listbox with tasks previously saved
    for task in tasks:
        task_listbox.insert(tk.END, task["name"])

    window.mainloop()

if __name__ == "__main__":
    main()