"""API-тесты для эндпоинта /store/order публичного Swagger Petstore.

Документация: https://petstore.swagger.io/
Адрес можно переопределить переменной окружения PETSTORE_URL.
"""
import os
import random

import pytest
import requests

BASE_URL = os.getenv("PETSTORE_URL", "https://petstore.swagger.io/v2")
ORDER_URL = f"{BASE_URL}/store/order"
TIMEOUT = 10


def make_order(order_id: int) -> dict:
    """Корректное тело заказа с заданным id."""
    return {
        "id": order_id,
        "petId": order_id,
        "quantity": 1,
        "shipDate": "2026-05-14T09:24:18.340Z",
        "status": "placed",
        "complete": True,
    }


@pytest.fixture
def order_id() -> int:
    """Случайный id: Petstore общий для всех, поэтому фиксированный id может быть занят."""
    return random.randint(10_000_000, 99_999_999)


def test_create_order_success(order_id):
    """Позитив: заказ создаётся, в ответе те же данные."""
    payload = make_order(order_id)

    response = requests.post(ORDER_URL, json=payload, timeout=TIMEOUT)

    assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}"
    data = response.json()
    assert data["id"] == order_id, "ID заказа не совпадает"
    assert data["status"] == "placed", f"Статус заказа не 'placed', а '{data['status']}'"
    assert data["complete"] is True, "Поле complete должно быть True"


def test_get_created_order(order_id):
    """Создали заказ, затем получили его по id: данные совпадают."""
    payload = make_order(order_id)
    created = requests.post(ORDER_URL, json=payload, timeout=TIMEOUT)
    assert created.status_code == 200

    response = requests.get(f"{ORDER_URL}/{order_id}", timeout=TIMEOUT)

    assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}"
    data = response.json()
    assert data["id"] == order_id
    assert data["petId"] == payload["petId"]
    assert data["quantity"] == payload["quantity"]
    assert data["status"] == payload["status"]


def test_get_nonexistent_order_returns_404(order_id):
    """Негатив: заказа с таким id нет, ожидаем 404 и сообщение об ошибке."""
    response = requests.get(f"{ORDER_URL}/{order_id}", timeout=TIMEOUT)

    assert response.status_code == 404, f"Ожидали 404, получили {response.status_code}"
    assert "not found" in response.json().get("message", "").lower()


@pytest.mark.parametrize(
    "field, bad_value",
    [
        ("id", "not-a-number"),
        ("quantity", "many"),
        ("complete", "maybe"),
    ],
)
def test_create_order_with_invalid_data(order_id, field, bad_value):
    """Негатив: значение неверного типа не должно приводить к успешному созданию заказа.

    По спецификации Petstore ожидается 400, на практике публичный сервис
    может вернуть 500, поэтому проверяем любой код ошибки (4xx/5xx), а не 200.
    """
    payload = make_order(order_id)
    payload[field] = bad_value

    response = requests.post(ORDER_URL, json=payload, timeout=TIMEOUT)

    assert response.status_code >= 400, (
        f"Заказ с некорректным полем '{field}'={bad_value!r} принят: {response.status_code}"
    )
