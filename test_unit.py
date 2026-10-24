# Сама функция, которую мы хотим протестировать
def calculate_price(price, discount):
    return price - discount


# Сам тест
def test_discount_calculation():
    # Вызываем функцию с тестовыми данными
    result = calculate_price(100, 20)

    # Проверяем результат с помощью обычного assert
    assert result == 80
