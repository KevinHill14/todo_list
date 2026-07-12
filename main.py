import tkinter as tk
from tkinter import ttk
from tasks import load_tasks, save_all_tasks, sort_tasks
from config import load_config, save_config
import ctypes


# Define the themes
# NOTE - You could reassign the colours, its fully customizable, but its preset as light and dark
THEMES = {
    "light": {
        "bg": "SystemButtonFace",
        "fg": "black",
        "entry_bg": "white",
        "row_bg": "SystemButtonFace",
        "row_starred": "#fff9c4",
        "row_completed": "#787878",
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "white",
        "entry_bg": "#3c3c3c",
        "row_bg": "#3c3c3c",
        "row_starred": "#5c5731",
        "row_completed": "#1e1e1e",
    },
}

# List of all side bar buttons
side_bar_buttons = []

# Shared state: tracks which task index is currently loaded into the entry box for editing (None = not editing)
editing_index = {"index": None}

# Track if a current popup is open
help_window_ref = {"window": None}
warning_window_ref = {"window": None}

# Set the windows bar to match the current theme
def set_titlebar_theme(window, dark):
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        value = ctypes.c_int(1 if dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
        )
    except Exception:
        pass  # Fails silently on unsupported Windows versions


# Return the current colour theme
def current_theme():
    return THEMES["dark"] if config.get("dark_mode") else THEMES["light"]


# Refresh all displayed tasks
def refresh_task_list():
    for widget in task_list_frame.winfo_children():
        widget.destroy()
    row_frames.clear()

    tasks = load_tasks()
    tasks = sort_tasks(tasks)

    if config["hide_completed"]:
        tasks = [t for t in tasks if not t.get("completed")]

    for i, task in enumerate(tasks):
        render_task_row(task, i)

    # Fix ghost frames
    task_list_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.update()


# Bring current task to the entry box
def start_edit(index, task_name):
    editing_index["index"] = index
    entry.delete(0, tk.END)
    entry.insert(0, task_name)
    entry.focus_set()


# Add a task to the list
def add_task():
    task_name = entry.get()
    if task_name.strip() == "":
        return
    entry.delete(0, tk.END)

    tasks = load_tasks()

    # Check if editing is enabled, if yes update that task, otherwise add new one
    if editing_index["index"] is not None:
        tasks[editing_index["index"]]["name"] = task_name
        editing_index["index"] = None
    else:
        tasks.append({"name": task_name, "due_date": "", "priority": "", "starred": False, "completed": False})

    save_all_tasks(tasks)
    refresh_task_list()
    entry.focus_set()


# Delete a task at a given index
def delete_task(index):
    tasks = load_tasks()
    tasks.pop(index)
    save_all_tasks(tasks)
    refresh_task_list()


# Prioritize a task and reorganize
def toggle_star(index):
    tasks = load_tasks()
    tasks[index]["starred"] = not tasks[index].get("starred")
    tasks = sort_tasks(tasks)
    save_all_tasks(tasks)
    refresh_task_list()


# Toggle a task to be completed and reorganize
def toggle_complete(index):
    tasks = load_tasks()
    tasks[index]["completed"] = not tasks[index].get("completed")
    tasks = sort_tasks(tasks)
    save_all_tasks(tasks)
    refresh_task_list()


# Update where a drag started
def start_drag(event, index):
    drag_data["index"] = index
    drag_data["row"] = row_frames[index]


# Logic for dragging tasks around
def on_drag_motion(event):
    widget_under_mouse = task_list_frame.winfo_containing(event.x_root, event.y_root)
    if widget_under_mouse is None:
        return

    # Move up parent chain until you find a frame
    target_row = widget_under_mouse
    while target_row is not None and target_row not in row_frames:
        target_row = target_row.master

    # Found a valid row
    if target_row in row_frames:
        target_index = row_frames.index(target_row)
        # Check if its a new row, if yes update position
        if target_index != drag_data["index"]:
            tasks = load_tasks()
            moved_task = tasks.pop(drag_data["index"])
            tasks.insert(target_index, moved_task)
            save_all_tasks(tasks)
            drag_data["index"] = target_index
            refresh_task_list()


# Determine if the user has enabled warning popups for clear all
def handle_clear_click():
    if config.get("warn_on_clear", True):
        clear_warning()
    else:
        clear_tasks()


# Render a single task row
def render_task_row(task, index):
    theme = current_theme()
    bg_color = theme["row_completed"] if task.get("completed") else theme["row_starred"] if task.get("starred") else theme["row_bg"]
    fg_color = theme["fg"]

    row = tk.Frame(task_list_frame, relief="raised", borderwidth=1, bg=bg_color)
    row.pack(fill="x", pady=2)
    row_frames.append(row)

    handle = tk.Label(row, text="☰", cursor="fleur", bg=bg_color, fg=fg_color)
    handle.pack(side="left", padx=5)

    label = tk.Label(row, text=task["name"], anchor="w", bg=bg_color, fg=fg_color)
    label.pack(side="left", fill="x", expand=True)
    label.bind("<Double-Button-1>", lambda event: start_edit(index, task["name"]))

    star_text = "★" if task.get("starred") else "☆"
    star_button = tk.Button(row, text=star_text, command=lambda: toggle_star(index), bg=bg_color, fg=fg_color)
    star_button.pack(side="right", padx=2)

    mark_completed_text = "✔" if not task.get("completed") else "⟲"
    mark_completed_button = tk.Button(row, text=mark_completed_text, command=lambda: toggle_complete(index), bg=bg_color, fg=fg_color)
    mark_completed_button.pack(side="right", padx=2)

    trash_button = tk.Button(row, text="🗑", command=lambda: delete_task(index), bg=bg_color, fg=fg_color)
    trash_button.pack(side="right")

    handle.bind("<Button-1>", lambda event: start_drag(event, index))
    handle.bind("<B1-Motion>", lambda event: on_drag_motion(event))


# Update the colour theme of every container and element
def apply_theme():
    theme = current_theme()
    set_titlebar_theme(window, config.get("dark_mode", False))
    window.config(bg=theme["bg"])
    main_frame.config(bg=theme["bg"])
    sidebar.config(bg=theme["bg"])
    content.config(bg=theme["bg"])
    entry.config(bg=theme["entry_bg"], fg=theme["fg"], insertbackground=theme["fg"])
    canvas.config(bg=theme["bg"])
    task_list_frame.config(bg=theme["bg"])

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Vertical.TScrollbar",
                     background=theme["bg"],
                     troughcolor=theme["bg"],
                     bordercolor=theme["bg"],
                     arrowcolor=theme["fg"])

    # Loop through each side bar button and colour it
    for btn in side_bar_buttons:
        btn.config(bg=theme["bg"], fg=theme["fg"])


# Invert the current theme and update colours
def toggle_dark_mode():
    config["dark_mode"] = not config.get("dark_mode")
    save_config(config)
    apply_theme()
    refresh_task_list()


# Clear all tasks displayed and in the json file
def clear_tasks():
    save_all_tasks([])
    refresh_task_list()


# Clear only completed tasks
def clear_completed():
    tasks = load_tasks()
    tasks = [t for t in tasks if not t.get("completed")]
    save_all_tasks(tasks)
    refresh_task_list()


# Display a warning before wiping the json file and all tasks
def clear_warning():
    if warning_window_ref["window"] is not None and warning_window_ref["window"].winfo_exists():
        warning_window_ref["window"].lift()
        return

    # Update colour theme of the warning popup
    theme = current_theme()
    warning_window = tk.Toplevel(window)
    warning_window_ref["window"] = warning_window
    warning_window.title("Warning")
    warning_window.geometry("300x100")
    warning_window.config(bg=theme["bg"])
    warning_window.update_idletasks()
    set_titlebar_theme(warning_window, config.get("dark_mode", False))

    label = tk.Label(warning_window, text="Are you sure you want to clear all tasks?",
                      bg=theme["bg"], fg=theme["fg"])
    label.pack(pady=10)

    button_frame = tk.Frame(warning_window, bg=theme["bg"])
    button_frame.pack()

    yes_button = tk.Button(button_frame, text="Yes", command=lambda: [clear_tasks(), warning_window.destroy()],
                            bg=theme["bg"], fg=theme["fg"])
    yes_button.pack(side="left", padx=10)

    no_button = tk.Button(button_frame, text="No", command=warning_window.destroy,
                           bg=theme["bg"], fg=theme["fg"])
    no_button.pack(side="right", padx=10)

    warning_window.bind("<Escape>", lambda event: warning_window.destroy())
    warning_window.focus_set()


# Show a help menu, with binds and shortcuts
def show_help():
    if help_window_ref["window"] is not None and help_window_ref["window"].winfo_exists():
        help_window_ref["window"].lift()
        return

    # Update colour theme of the help menu
    theme = current_theme()
    help_window = tk.Toplevel(window)
    help_window_ref["window"] = help_window
    help_window.title("Help")
    help_window.geometry("320x400")
    help_window.config(bg=theme["bg"])
    help_window.update_idletasks()
    set_titlebar_theme(help_window, config.get("dark_mode", False))

    help_text = (
        "Keybinds & Controls:\n\n"
        "Enter — Add typed task (or save an edit)\n"
        "Double-click a task — Edit its name\n"
        "Escape — Open Clear All warning / close this window\n"
        "☰ (drag handle) — Reorder tasks\n"
        "★ — Prioritize a task\n"
        "✔ / ⟲ — Mark complete / restore\n"
        "🗑 — Delete task\n"
        "Mouse wheel — Scroll task list\n\n"
        "Sidebar:\n"
        "? — This help menu\n"
        "👁 — Hide/show completed tasks\n"
        "✔🗑 — Clear completed tasks\n"
        "🗑 — Clear all tasks\n"
        "⚠ — Toggle clear-all warning\n"
        "🌙 — Toggle dark mode"
    )

    label = tk.Label(help_window, text=help_text, justify="left", anchor="w",
                      bg=theme["bg"], fg=theme["fg"])
    label.pack(padx=15, pady=15, fill="both", expand=True)

    close_button = tk.Button(help_window, text="Got it", command=help_window.destroy,
                              bg=theme["bg"], fg=theme["fg"])
    close_button.pack(pady=5)

    help_window.bind("<Escape>", lambda event: help_window.destroy())
    help_window.focus_set()
    

# Toggle the config to hide / show completed tasks
def toggle_hide_completed():
    config["hide_completed"] = not config["hide_completed"]
    save_config(config)

    theme = current_theme()
    if config["hide_completed"]:
        hide_completed_button.config(bg=theme["row_completed"], fg=theme["fg"], relief="sunken")
    else:
        hide_completed_button.config(bg=theme["bg"], fg=theme["fg"], relief="raised")

    refresh_task_list()


# Toggle the config to hide / show clear all warning popup
def toggle_warn_on_clear():
    config["warn_on_clear"] = not config.get("warn_on_clear", True)
    save_config(config)

    theme = current_theme()
    if config["warn_on_clear"]:
        warn_toggle_button.config(bg=theme["bg"], fg=theme["fg"], relief="raised")
    else:
        warn_toggle_button.config(bg=theme["row_completed"], fg=theme["fg"], relief="sunken")


# Main loop and logic
def main():
    global entry, task_list_frame, row_frames, drag_data, config, hide_completed_button, warn_toggle_button, main_frame, sidebar, content, canvas, window
    config = load_config()

    row_frames = []
    drag_data = {"index": None, "row": None}

    window = tk.Tk()
    window.title("My Todo List")
    window.geometry("450x400")

    # Show help menu on first use
    if not config["initial_entry"]:
        show_help()
        config["initial_entry"] = True
        save_config(config)

    # Main horizontal split
    main_frame = tk.Frame(window)
    main_frame.pack(fill="both", expand=True)

    # Create the left side bar for buttons
    sidebar = tk.Frame(main_frame, width=50)
    sidebar.pack(side="left", fill="y", padx=(8, 4), pady=8)

    initial_bg = "#cccccc" if config["hide_completed"] else "SystemButtonFace"
    initial_relief = "sunken" if config["hide_completed"] else "raised"

    # Create side bar buttons (Order matters)
    # NOTE - You can move the buttons around to customize the layout by changing where their pair exists
    help_button = tk.Button(sidebar, text="?", width=3, command=show_help)
    help_button.pack(pady=2)
    side_bar_buttons.append(help_button)

    hide_completed_button = tk.Button(sidebar, text="👁", width=3, command=toggle_hide_completed, bg=initial_bg, relief=initial_relief)
    hide_completed_button.pack(pady=2)
    side_bar_buttons.append(hide_completed_button)

    clear_completed_button = tk.Button(sidebar, text="✔🗑", width=3, command=clear_completed)
    clear_completed_button.pack(pady=2)
    side_bar_buttons.append(clear_completed_button)

    clear_button = tk.Button(sidebar, text="🗑", width=3, command=handle_clear_click)
    clear_button.pack(pady=2)
    side_bar_buttons.append(clear_button)

    warn_toggle_button = tk.Button(sidebar, text="⚠", width=3, command=toggle_warn_on_clear)
    warn_toggle_button.pack(pady=2)
    side_bar_buttons.append(warn_toggle_button)

    dark_mode_button = tk.Button(sidebar, text="🌙", width=3, command=toggle_dark_mode)
    dark_mode_button.pack(pady=2)
    side_bar_buttons.append(dark_mode_button)

    # Create content block
    content = tk.Frame(main_frame)
    content.pack(side="left", fill="both", expand=True, padx=(4, 8), pady=8)

    # Create the entry block
    entry = tk.Entry(content, width=30)
    entry.pack(fill="x", pady=(0, 8))
    entry.bind("<Return>", lambda event: add_task())
    entry.bind("<Escape>", lambda event: clear_warning())
    entry.focus_set()

    # Scrollable task setup
    canvas = tk.Canvas(content)
    scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
    task_list_frame = tk.Frame(canvas)

    task_list_frame.bind(
        "<Configure>",
        lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas_window = canvas.create_window((0, 0), window=task_list_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def resize_frame(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", resize_frame)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

    # Wait for window to appear before continuing
    window.update_idletasks()
    apply_theme()
    refresh_task_list()

    window.mainloop()
    

if __name__ == "__main__":
    main()

