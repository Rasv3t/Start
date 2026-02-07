income = float(input('Ваш доход за месяц: '))

expenses = []

while True:
    waste = input('Введите название траты(или "стоп" для выхода): ')
    if waste == "стоп":
        break
    amount = int(input('Введите сумму: '))

    expense = {'waste': waste, 'amount': amount}
    expenses.append(expense)

print('\n' + '='*40)
print('Ваши траты:')

total = 0
max_amount = 0
max_waste = ''

for i, expense in enumerate(expenses, 1):
    print(f"{i}. {expense['waste']} — {expense['amount']} руб.")
    total += expense['amount']
    
    if expense['amount'] > max_amount:
        max_amount = expense['amount']
        max_waste = expense['waste']

print(f"\nВсего потрачено: {total} руб.")

if total <= income:
    remainder = income - total
    print(f"✅ Вы в рамках бюджета. Остаток: {remainder} руб.")
else:
    overspend = total - income
    print(f"⚠️ Вы превысили бюджет на {overspend} руб.")

if max_waste:
    print(f"Самая крупная трата: {max_waste} ({max_amount} руб.)")
