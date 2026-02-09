from data_manager import load_tasks, save_tasks, get_next_id
import datetime

def print_menu():
    """Выводит меню."""
    print("\n" + "="*40)
    print("🎯 УМНЫЙ ТРЕКЕР ЗАДАЧ")
    print("="*40)
    print("1. 📝 Добавить задачу")
    print("2. 📋 Показать все задачи")
    print("3. 🔍 Найти задачу")
    print("4. ✅ Отметить как выполненную")
    print("5. 🗑️ Удалить задачу")
    print("6. 📊 Статистика")
    print("0. 🚪 Выйти")
    print("="*40)

def add_task(tasks):
    """Добавляет новую задачу."""
    print("\n➕ ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ")
    
    name = input("Введите описание задачи: ").strip()
    if not name:
        print("⚠️ Описание не может быть пустым!")
        return tasks
    
    # Получаем приоритет
    while True:
        try:
            priority = int(input("Приоритет (1-5, где 1 - самый высокий): "))
            if 1 <= priority <= 5:
                break
            else:
                print("⚠️ Приоритет должен быть от 1 до 5!")
        except ValueError:
            print("⚠️ Введите число!")
    
    # Получаем дедлайн (опционально)
    deadline = input("Дедлайн (ДД.ММ.ГГГГ или Enter чтобы пропустить): ").strip()
    
    # Создаем задачу
    task = {
        "id": get_next_id(),
        "name": name,
        "priority": priority,
        "completed": False,
        "created_at": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "deadline": deadline if deadline else None
    }
    
    tasks.append(task)
    print(f"✅ Задача #{task['id']} добавлена!")
    return tasks

def show_tasks(tasks, title="ВСЕ ЗАДАЧИ"):
    """Показывает список задач."""
    if not tasks:
        print("📭 Список задач пуст!")
        return
    
    print(f"\n📋 {title}")
    print("-" * 50)
    
    # Сортируем: сначала невыполненные, потом по приоритету
    sorted_tasks = sorted(tasks, key=lambda x: (x["completed"], x["priority"]))
    
    for task in sorted_tasks:
        status = "✅" if task["completed"] else "⏳"
        priority_stars = "★" * task["priority"] + "☆" * (5 - task["priority"])
        
        print(f"#{task['id']} {task['name']}")
        print(f"   Приоритет: {priority_stars} | Статус: {status}")
        print(f"   Создана: {task['created_at']}")
        if task.get("deadline"):
            print(f"   📅 Дедлайн: {task['deadline']}")
        print()

def find_tasks(tasks):
    """Ищет задачи по ключевому слову."""
    if not tasks:
        print("📭 Нет задач для поиска!")
        return
    
    keyword = input("Введите слово для поиска: ").lower().strip()
    if not keyword:
        print("⚠️ Введите слово для поиска!")
        return
    
    found = [task for task in tasks if keyword in task["name"].lower()]
    
    if found:
        show_tasks(found, f"НАЙДЕНО: {len(found)} ЗАДАЧ")
    else:
        print(f"🔍 Задачи с словом '{keyword}' не найдены!")

def complete_task(tasks):
    """Отмечает задачу как выполненную."""
    if not tasks:
        print("📭 Нет задач!")
        return tasks
    
    show_tasks(tasks)
    
    try:
        task_id = int(input("\nВведите ID задачи для отметки: "))
        for task in tasks:
            if task["id"] == task_id:
                if task["completed"]:
                    print("⚠️ Эта задача уже выполнена!")
                else:
                    task["completed"] = True
                    task["completed_at"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                    print(f"✅ Задача '#{task_id}' отмечена как выполненная!")
                return tasks
        
        print("⚠️ Задача с таким ID не найдена!")
    except ValueError:
        print("⚠️ Введите числовой ID!")
    
    return tasks

def delete_task(tasks):
    """Удаляет задачу."""
    if not tasks:
        print("📭 Нет задач!")
        return tasks
    
    show_tasks(tasks)
    
    try:
        task_id = int(input("\nВведите ID задачи для удаления: "))
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                deleted_name = task["name"]
                del tasks[i]
                print(f"🗑️ Задача '#{task_id}' удалена!")
                return tasks
        
        print("⚠️ Задача с таким ID не найдена!")
    except ValueError:
        print("⚠️ Введите числовой ID!")
    
    return tasks

def show_statistics(tasks):
    """Показывает статистику."""
    if not tasks:
        print("📭 Нет данных для статистики!")
        return
    
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    pending = total - completed
    
    print("\n📊 СТАТИСТИКА")
    print("-" * 30)
    print(f"Всего задач: {total}")
    print(f"Выполнено: {completed} ({completed/total*100:.1f}%)")
    print(f"Осталось: {pending} ({pending/total*100:.1f}%)")
    
    # Задачи с дедлайнами
    with_deadline = [task for task in tasks if task.get("deadline")]
    if with_deadline:
        print(f"\n📅 Задач с дедлайном: {len(with_deadline)}")
        for task in with_deadline:
            if not task["completed"]:
                print(f"  • #{task['id']} {task['name']} → до {task['deadline']}")

def main():
    """Главная функция."""
    print("🚀 Загружаем задачи из файла...")
    tasks = load_tasks()
    print(f"✅ Загружено задач: {len(tasks)}")
    
    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "0":
            save_tasks(tasks)
            print("👋 До свидания! Данные сохранены.")
            break
        
        elif choice == "1":
            tasks = add_task(tasks)
        
        elif choice == "2":
            show_tasks(tasks)
        
        elif choice == "3":
            find_tasks(tasks)
        
        elif choice == "4":
            tasks = complete_task(tasks)
        
        elif choice == "5":
            tasks = delete_task(tasks)
        
        elif choice == "6":
            show_statistics(tasks)
        
        else:
            print("⚠️ Неверный выбор! Попробуйте снова.")
        
        # Автосохранение после каждого действия
        if choice in ["1", "4", "5"]:
            save_tasks(tasks)

if __name__ == "__main__":
    main()