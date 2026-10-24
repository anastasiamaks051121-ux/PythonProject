# PythonProject

Учебный репозиторий по Python и автоматизации тестирования (QA).

- `tests/` — API-тесты на pytest + requests для `/store/order` публичного [Swagger Petstore](https://petstore.swagger.io/): позитивный сценарий, получение заказа, несуществующий заказ (404), некорректные данные.
- `practice/` — учебные скрипты (логические задачи, консольная игра на curses, наброски UI-теста).
- Запуск: `pip install -r requirements.txt`, затем `pytest -v`. Адрес API можно сменить переменной `PETSTORE_URL`.
