import json
import tkinter as tk


def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
        return tasks
    except FileNotFoundError:
        return []


def save_all_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)


def add_task():
    task_name = entry.get()
    if task_name.strip() == "":
        return
    entry.delete(0, tk.END)

    tasks = load_tasks()
    tasks.append({"name": task_name, "due_date": "", "priority": ""})
    save_all_tasks(tasks)

    refresh_task_list()  # rebuild so drag bindings apply to the new row too


def delete_task(index):
    tasks = load_tasks()
    tasks.pop(index)
    save_all_tasks(tasks)
    refresh_task_list()


def start_drag(event, index):
    drag_data["index"] = index
    drag_data["row"] = row_frames[index]


def on_drag_motion(event, index):
    # Figure out which row we're currently hovering over based on mouse Y position
    widget_under_mouse = task_list_frame.winfo_containing(event.x_root, event.y_root)
    if widget_under_mouse is None:
        return

    # Walk up to find which row Frame this widget belongs to
    target_row = widget_under_mouse
    while target_row is not None and target_row not in row_frames:
        target_row = target_row.master

    if target_row in row_frames:
        target_index = row_frames.index(target_row)
        if target_index != drag_data["index"]:
            # Reorder the underlying task list
            tasks = load_tasks()
            moved_task = tasks.pop(drag_data["index"])
            tasks.insert(target_index, moved_task)
            save_all_tasks(tasks)
            drag_data["index"] = target_index
            refresh_task_list()


def render_task_row(task_name, index):
    row = tk.Frame(task_list_frame, relief="raised", borderwidth=1)
    row.pack(fill="x", pady=2)
    row_frames.append(row)

    handle = tk.Label(row, text="☰", cursor="fleur")  # drag handle icon
    handle.pack(side="left", padx=5)

    label = tk.Label(row, text=task_name, anchor="w")
    label.pack(side="left", fill="x", expand=True)

    trash_button = tk.Button(row, text="🗑", command=lambda: delete_task(index))
    trash_button.pack(side="right")

    # Bind drag events to the handle
    handle.bind("<Button-1>", lambda event: start_drag(event, index))
    handle.bind("<B1-Motion>", lambda event: on_drag_motion(event, index))


def refresh_task_list():
    for widget in task_list_frame.winfo_children():
        widget.destroy()
    row_frames.clear()

    tasks = load_tasks()
    for i, task in enumerate(tasks):
        render_task_row(task["name"], i)


def clear_tasks():
    save_all_tasks([])
    refresh_task_list()


def main():
    global entry, task_list_frame, row_frames, drag_data

    row_frames = []  # keeps track of every row Frame, in order
    drag_data = {"index": None, "row": None}  # tracks what's currently being dragged

    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("400x400")

    entry = tk.Entry(window, width=30)
    entry.pack(pady=10)
    entry.bind("<Return>", lambda event: add_task())
    entry.focus_set()

    add_button = tk.Button(window, text="Add Task", command=add_task)
    add_button.pack()

    clear_button = tk.Button(window, text="Clear Tasks", command=clear_tasks)
    clear_button.pack(pady=5)
    entry.bind("<Escape>", lambda event: clear_tasks())

    task_list_frame = tk.Frame(window)
    task_list_frame.pack(fill="both", expand=True, pady=10)

    refresh_task_list()

    window.mainloop()


if __name__ == "__main__":
    main()