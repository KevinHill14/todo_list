import json

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
    # Completed tasks always go last, regardless of starred status
    active = [t for t in tasks if not t.get("completed")]
    completed = [t for t in tasks if t.get("completed")]

    # Within active tasks, starred ones go first
    starred = [t for t in active if t.get("starred")]
    unstarred = [t for t in active if not t.get("starred")]

    return starred + unstarred + completed