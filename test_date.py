from datetime import datetime, date

def test_date_input(user_input):
    try:
        target_date = datetime.strptime(user_input.strip(), "%d.%m.%Y").date()
    except ValueError:
        return f"❌ Неверный формат. Используйте: ДД.МММ.ГГГГ\nНапример: 16.05.2026"

    today = date.today()
    if target_date < today:
        return f"❌ Дата должна быть в будущем"

    return f"✅ Дата принята: {target_date.strftime('%d.%m.%Y')}"

# Test cases
print("Test 1 - Valid future date:")
print(test_date_input("20.06.2026"))

print("\nTest 2 - Invalid format:")
print(test_date_input("16/05/2026"))

print("\nTest 3 - Past date:")
print(test_date_input("01.01.2020"))

print("\nTest 4 - Today:")
print(test_date_input("16.05.2026"))
