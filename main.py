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


def sort_tasks(tasks):
    # Starred tasks first, but keep relative order within each group
    starred = [t for t in tasks if t.get("starred")]
    unstarred = [t for t in tasks if not t.get("starred")]
    return starred + unstarred


def add_task():
    task_name = entry.get()
    if task_name.strip() == "":
        return
    entry.delete(0, tk.END)

    tasks = load_tasks()
    tasks.append({"name": task_name, "due_date": "", "priority": "", "starred": False})
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
    bg_color = "#fff9c4" if task.get("starred") else "SystemButtonFace"
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

    trash_button = tk.Button(row, text="🗑", command=lambda: delete_task(index), bg=bg_color)
    trash_button.pack(side="right")

    handle.bind("<Button-1>", lambda event: start_drag(event, index))
    handle.bind("<B1-Motion>", lambda event: on_drag_motion(event, index))


def refresh_task_list():
    for widget in task_list_frame.winfo_children():
        widget.destroy()
    row_frames.clear()

    tasks = load_tasks()
    for i, task in enumerate(tasks):
        render_task_row(task, i)


def clear_tasks():
    save_all_tasks([])
    refresh_task_list()


def main():
    global entry, task_list_frame, row_frames, drag_data

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

    clear_button = tk.Button(window, text="Clear Tasks", command=clear_tasks)
    clear_button.pack(pady=5)
    entry.bind("<Escape>", lambda event: clear_tasks())

    task_list_frame = tk.Frame(window)
    task_list_frame.pack(fill="both", expand=True, pady=10)

    refresh_task_list()

    window.mainloop()


if __name__ == "__main__":
    main()