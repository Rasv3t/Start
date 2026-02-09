tasks = []

print('Ваш список дел')

print('\n' + '='*40)

while True:
    name_task = input('Введите вашу задачу (или "готово"):')
    if name_task == 'готово':
        break
    priority = int(input('Введите приоритет задачи (начиная с 1):'))
    tasks.append((priority, name_task))
    print('Ваша задача добавлена в список дел')

tasks.sort(key=lambda x: x[0])

for i, (priority, task) in enumerate(tasks, 1):
    print(f'{i}. [{priority}] {task}')