#from selenium.webdriver.common.by import By
# from selenium.webdriver.remote.webdriver import WebDriver
#
# def test_name_field(driver: WebDriver):
#     # Предполагаем, что есть элемент поля ввода 'Имя' с id='name_input'
#     name_field = driver.find_element(By.ID, "name_input")
#
#     # Позитивный тест: допустимое имя
#     name_field.send_keys("Иван Иванов")
#     # Проверка отсутствия ошибок валидации
#
#     # Очистка поля
#     name_field.clear()
#
#     # Негативный тест: недопустимые символы (цифры)
#     name_field.send_keys("12345")
#     # Проверка появления сообщения об ошибке
#
#     # Очистка поля
#     name_field.clear()
#
#     # Негативный тест: пустая строка
#     name_field.send_keys("")
#     # Проверка сообщения об обязательности поля
from pyexpat.errors import messages

# num="1"
# num2="2"
# total=num+num2
# print(total)
#
# lol = 'хо'
# print(lol * 10)
#
# one_hundred = 100
# print(onehundred)

speed_kmh = 1079252848.8

# переменную speed_kms сделайте типа int
speed_kms = int(speed_kmh/3600)

print('Скорость света равна', speed_kms, 'км/с')

