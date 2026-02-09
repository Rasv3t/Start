guests = []

while True:
    name = input('Введите имя гостя(или "готово"):')
    if name == 'готово':
        break
    guests.append(name)
    print(f'Гость {name} добавлен')

print('Ваш список гостей:')

if len(guests) == 0:
        print('Гостей нет')

for i, guest in enumerate(guests, 1):
    print(f'{i}. {guest}')
