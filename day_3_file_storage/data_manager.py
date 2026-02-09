import json
import os

# Константа - имя файла для хранения данных
DATA_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            tasks = json.load(file)
            return tasks
    except (json.JSONDecodeError, FileNotFoundError):
        # Если файл поврежден или пустой
        return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(tasks, file, ensure_ascii=False, indent=2)
    print("💾 Данные сохранены!")

def add_task_to_file(task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

def get_next_id():
    tasks = load_tasks()
    if not tasks:
        return 1
    # Находим максимальный ID среди существующих задач
    max_id = max(task.get("id", 0) for task in tasks)
    return max_id + 1