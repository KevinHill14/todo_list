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


# Save all the tasks to the JSON file
def save_all_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)


# Add a new task to the list and update the GUI
def add_task():
    task_name = entry.get()
    if task_name.strip() == "":
        return
    entry.delete(0, tk.END)

    # Update the JSON
    tasks = load_tasks()
    tasks.append({"name": task_name, "due_date": "", "priority": ""})
    save_all_tasks(tasks)

    render_task_row(task_name, len(tasks) - 1)


# Delete a task from the list and update the GUI
def delete_task(index, row_frame):
    tasks = load_tasks()
    tasks.pop(index)
    save_all_tasks(tasks)
    row_frame.destroy()
    refresh_task_list()


# Render a single task row in the GUI
def render_task_row(task_name, index):
    row = tk.Frame(task_list_frame)
    row.pack(fill="x", pady=2)

    label = tk.Label(row, text=task_name, anchor="w")
    label.pack(side="left", fill="x", expand=True)

    trash_button = tk.Button(row, text="🗑", command=lambda: delete_task(index, row))
    trash_button.pack(side="right")


# Refresh the current task list
def refresh_task_list():
    # Clear all rows currently shown
    for widget in task_list_frame.winfo_children():
        widget.destroy()
    # Re-render from the file, so indexes match task order
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        render_task_row(task["name"], i)


# Clear all tasks
def clear_tasks():
    save_all_tasks([])
    refresh_task_list()


# Main logic
def main():
    global entry, task_list_frame

    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("400x400")

    entry = tk.Entry(window, width=30)
    entry.pack(pady=10)

    add_button = tk.Button(window, text="Add Task", command=add_task)
    add_button.pack()

    clear_button = tk.Button(window, text="Clear Tasks", command=clear_tasks)
    clear_button.pack(pady=5)

    task_list_frame = tk.Frame(window)
    task_list_frame.pack(fill="both", expand=True, pady=10)

    refresh_task_list()

    window.mainloop()


if __name__ == "__main__":
    main()