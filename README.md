# To-Do Lite

A simple, lightweight desktop to-do list app for Windows. No accounts, no bloat, no internet connection required — just a fast, clean task list that stays out of your way.

Built with Python and Tkinter. Runs at around 36MB of RAM.

## Features

- Add, edit, and delete tasks
- Star tasks to prioritize them (auto-sorts to the top)
- Mark tasks complete without losing them — restore anytime
- Drag and drop to manually reorder tasks
- Hide completed tasks with one click
- Dark mode (including the window title bar)
- Optional confirmation warning before clearing all tasks
- Everything saves automatically to a local file — no sign-in, no cloud, no tracking
- Scrollable list, resizable window

## Download

Grab the latest version from the [Releases page](https://github.com/KevinHill14/todo_list/releases) — download `TodoList.exe` and run it. No installation or Python required.

> **Note:** Windows may show a "Windows protected your PC" SmartScreen warning when you first run it, since the app isn't digitally signed. This is expected for small independent projects — click **More info** → **Run anyway** to continue.

Your tasks and settings are saved as `tasks.json` and `config.json` in the same folder as the `.exe`.

## Controls

| Action | How |
|---|---|
| Add a task | Type in the box, press **Enter** |
| Edit a task | Double-click its name |
| Reorder tasks | Drag using the ☰ handle |
| Prioritize a task | Click ★ |
| Complete / restore a task | Click ✔ / ⟲ |
| Delete a task | Click 🗑 |
| Scroll the list | Mouse wheel |

**Sidebar:**

| Icon | Action |
|---|---|
| ? | Open help |
| 👁 | Hide / show completed tasks |
| ✔🗑 | Clear completed tasks only |
| 🗑 | Clear all tasks |
| ⚠ | Toggle the "are you sure?" warning before clearing all |
| 🌙 | Toggle dark mode |

## Running from source

If you'd rather run it directly with Python instead of the `.exe`:

```
git clone https://github.com/KevinHill14/todo_list.git
cd todo_list
python main.py
```

Requires Python 3.9+ (no external packages needed — everything used is part of the Python standard library).

## Notes

This is a v1, intentionally kept simple and lightweight. Bigger features (due dates, categories, reminders, etc.) may come in a future extended version.

## License

Feel free to use, modify, or learn from this project.