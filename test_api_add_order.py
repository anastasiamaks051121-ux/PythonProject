import requests
import pytest

import requests


def test_create_order_success():
    # Проверка создания заказа через POST-запрос
    url = "https://petstore.swagger.io/v2/store/order"
    payload = {
        "id": 19999,
        "petId": 19999,
        "quantity": 0,
        "shipDate": "2026-05-14T09:24:18.340Z",
        "status": "placed",
        "complete": True
    }

    # Отправляем запрос
    response = requests.post(url, json=payload, timeout=10)

    assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}"

    data = response.json()
    assert data["status"] == "placed", f"Статус заказа не 'placed', а '{data['status']}'"
    assert data["complete"] == True, "Поле complete должно быть True"
    assert data["id"] == 19999, "ID заказа не совпадает"

    print(f" Тест пройден! Статус: {response.status_code}, Заказ: {data['id']}")