import json
import tkinter as tk


def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
        return tasks
    except FileNotFoundError:
        return []


def load_config():
    try:
        with open("config.json", "r") as file:
            configs = json.load(file)
        return configs
    except (FileNotFoundError, json.JSONDecodeError):
        return {"hide_completed": False, "initial_entry": False}

def save_all_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)


def sort_tasks(tasks):
    # Completed tasks always go last, regardless of starred status
    active = [t for t in tasks if not t.get("completed")]
    completed = [t for t in tasks if t.get("completed")]

    # Within active tasks, starred ones go first
    starred = [t for t in active if t.get("starred")]
    unstarred = [t for t in active if not t.get("starred")]

    return starred + unstarred + completed


def add_task():
    task_name = entry.get()
    if task_name.strip() == "":
        return
    entry.delete(0, tk.END)

    tasks = load_tasks()
    tasks.append({"name": task_name, "due_date": "", "priority": "", "starred": False, "completed": False})
    save_all_tasks(tasks)

    refresh_task_list()
    entry.focus_set()


def delete_task(index):
    tasks = load_tasks()
    tasks.pop(index)
    save_all_tasks(tasks)
    refresh_task_list()


def toggle_star(index):
    tasks = load_tasks()
    tasks[index]["starred"] = not tasks[index].get("starred")
    tasks = sort_tasks(tasks)  # re-sort immediately so it jumps to the top
    save_all_tasks(tasks)
    refresh_task_list()


def toggle_complete(index):
    tasks = load_tasks()
    tasks[index]["completed"] = not tasks[index].get("completed")
    tasks = sort_tasks(tasks)
    save_all_tasks(tasks)
    refresh_task_list()


def start_drag(event, index):
    drag_data["index"] = index
    drag_data["row"] = row_frames[index]


def on_drag_motion(event, index):
    widget_under_mouse = task_list_frame.winfo_containing(event.x_root, event.y_root)
    if widget_under_mouse is None:
        return

    target_row = widget_under_mouse
    while target_row is not None and target_row not in row_frames:
        target_row = target_row.master

    if target_row in row_frames:
        target_index = row_frames.index(target_row)
        if target_index != drag_data["index"]:
            tasks = load_tasks()
            moved_task = tasks.pop(drag_data["index"])
            tasks.insert(target_index, moved_task)
            save_all_tasks(tasks)
            drag_data["index"] = target_index
            refresh_task_list()


def render_task_row(task, index):
    bg_color = "#787878" if task.get("completed") else "#fff9c4" if task.get("starred") else "SystemButtonFace"
    row = tk.Frame(task_list_frame, relief="raised", borderwidth=1, bg=bg_color)
    row.pack(fill="x", pady=2)
    row_frames.append(row)

    handle = tk.Label(row, text="☰", cursor="fleur", bg=bg_color)
    handle.pack(side="left", padx=5)

    label = tk.Label(row, text=task["name"], anchor="w", bg=bg_color)
    label.pack(side="left", fill="x", expand=True)

    # Show a filled star if starred, hollow star if not
    star_text = "★" if task.get("starred") else "☆"
    star_button = tk.Button(row, text=star_text, command=lambda: toggle_star(index), bg=bg_color)
    star_button.pack(side="right", padx=2)

    # Create the mark completed button
    mark_completed_text= "✔" if not task.get("completed") else "⟲"
    mark_completed_button = tk.Button(row, text=mark_completed_text, command=lambda: toggle_complete(index), bg=bg_color)
    mark_completed_button.pack(side="right", padx=2)

    trash_button = tk.Button(row, text="🗑", command=lambda: delete_task(index), bg=bg_color)
    trash_button.pack(side="right")

    handle.bind("<Button-1>", lambda event: start_drag(event, index))
    handle.bind("<B1-Motion>", lambda event: on_drag_motion(event, index))


def refresh_task_list():
    for widget in task_list_frame.winfo_children():
        widget.destroy()
    row_frames.clear()

    tasks = load_tasks()
    if config["hide_completed"]:
        tasks = [t for t in tasks if not t.get("completed")]

    for i, task in enumerate(tasks):
        render_task_row(task, i)


def clear_tasks():
    save_all_tasks([])
    refresh_task_list()


def clear_completed():
    tasks = load_tasks()
    tasks = [t for t in tasks if not t.get("completed")]
    save_all_tasks(tasks)
    refresh_task_list()


def clear_warning():
    warning_window = tk.Toplevel()
    warning_window.title("Warning")
    warning_window.geometry("300x100")

    label = tk.Label(warning_window, text="Are you sure you want to clear all tasks?")
    label.pack(pady=10)

    button_frame = tk.Frame(warning_window)
    button_frame.pack()

    yes_button = tk.Button(button_frame, text="Yes", command=lambda: [clear_tasks(), warning_window.destroy()])
    yes_button.pack(side="left", padx=10)

    no_button = tk.Button(button_frame, text="No", command=warning_window.destroy)
    no_button.pack(side="right", padx=10)

    # Let Escape close the popup without needing the mouse
    warning_window.bind("<Escape>", lambda event: [warning_window.destroy(), clear_tasks()])
    warning_window.focus_set()  # make sure the popup actually receives key presses


def save_config(config):
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)


def toggle_hide_completed():
    config["hide_completed"] = not config["hide_completed"]
    save_config(config)
    refresh_task_list()

def main():
    global entry, task_list_frame, row_frames, drag_data, config
    config = load_config()

    row_frames = []
    drag_data = {"index": None, "row": None}

    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("400x400")

    entry = tk.Entry(window, width=30)
    entry.pack(pady=10)
    entry.bind("<Return>", lambda event: add_task())
    entry.focus_set()

    add_button = tk.Button(window, text="Add Task", command=add_task)
    add_button.pack()

    clear_button = tk.Button(window, text="Clear Tasks", command=clear_warning)
    clear_button.pack(pady=5)
    entry.bind("<Escape>", lambda event: clear_warning())

    clear_completed_button = tk.Button(window, text="Clear Completed", command=clear_completed)
    clear_completed_button.pack(pady=5)

    hide_completed_button = tk.Button(window, text="Hide Completed", command=toggle_hide_completed)
    hide_completed_button.pack(pady=5)

    task_list_frame = tk.Frame(window)
    task_list_frame.pack(fill="both", expand=True, pady=10)

    refresh_task_list()

    window.mainloop()


if __name__ == "__main__":
    main()