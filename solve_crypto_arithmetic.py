import itertools
import re
# Задача на логику. Нужно найти значения всех букв в простом примере на сложение 6 значных чисел.
# Каждая буква соответствует своей цифре, т.е. значения букв не могут совпадать.
# Задача решается в 10 системе счисления ). А = 5

#
# + А Б В Г Д А
#  Е Ж З Г Д А
#  З Б И Ж З У

def solve_crypto_arithmetic():
    print("=== УНИВЕРСАЛЬНЫЙ РЕШАТЕЛЬ ЗАДАЧ НА СЛОЖЕНИЕ ===")
    print("Правила: Каждая буква — уникальная цифра (0-9).")
    print("Первая буква числа не может быть 0.\n")

    # 1. Ввод данных
    word1 = input("Введите первое слагаемое (например, АБВГДА): ").strip().upper()
    word2 = input("Введите второе слагаемое (например, ЕЖЗГДА): ").strip().upper()
    word_sum = input("Введите сумму (например, ЗБИЖЗУ): ").strip().upper()

    # Ввод известных значений
    print("\nВведите известные значения букв в формате БУКВА=ЦИФРА.")
    print("Разделяйте пары запятой или пробелом. (Пример: А=5, Х=0)")
    known_input = input("Известные буквы (оставьте пустым, если нет): ").strip()

    known_map = {}
    if known_input:
        # Парсим ввод: "А=5, Б=3" -> {'А': 5, 'Б': 3}
        parts = re.split(r'[,\s]+', known_input)
        for part in parts:
            if '=' in part:
                k, v = part.split('=')
                k = k.strip().upper()
                v = int(v.strip())
                if 0 <= v <= 9:
                    known_map[k] = v
                else:
                    print(f"Ошибка: Цифра {v} недопустима.")
                    return

    # 2. Сбор всех уникальных букв
    all_text = word1 + word2 + word_sum
    unique_letters = list(set(all_text))

    if len(unique_letters) > 10:
        print(f"\n❌ Ошибка: Слишком много уникальных букв ({len(unique_letters)}). Максимум 10.")
        return

    # Проверка конфликтов в известных значениях
    for letter, val in known_map.items():
        if letter not in unique_letters:
            print(f"⚠️ Предупреждение: Буква '{letter}' есть в условиях, но нет в словах.")

    # Буквы, которые нужно найти
    unknown_letters = [l for l in unique_letters if l not in known_map]
    n_unknown = len(unknown_letters)

    # Доступные цифры (те, что не заняты известными буквами)
    used_digits = set(known_map.values())
    available_digits = [d for d in range(10) if d not in used_digits]

    if len(available_digits) < n_unknown:
        print(f"\n❌ Ошибка: Недостаточно свободных цифр для {n_unknown} неизвестных букв.")
        return

    # Первые буквы чисел не могут быть 0
    first_letters = {word1[0], word2[0], word_sum[0]}

    print(f"\n🔍 Поиск решения...")
    print(f"   Известно: {known_map}")
    print(f"   Ищем значения для: {unknown_letters}")
    print("-" * 30)

    # 3. Перебор вариантов (Permutations)
    # Генерируем все перестановки доступных цифр для неизвестных букв
    for perm in itertools.permutations(available_digits, n_unknown):
        # Создаем полное отображение: известные + текущая перестановка
        current_map = known_map.copy()
        current_map.update(dict(zip(unknown_letters, perm)))

        # Проверка: первые буквы не должны быть 0
        invalid_zero = False
        for letter in first_letters:
            if current_map.get(letter) == 0:
                invalid_zero = True
                break
        if invalid_zero:
            continue

        # Преобразование слов в числа
        try:
            num1 = int("".join(str(current_map[c]) for c in word1))
            num2 = int("".join(str(current_map[c]) for c in word2))
            total = int("".join(str(current_map[c]) for c in word_sum))
        except KeyError:
            continue

        # Проверка равенства
        if num1 + num2 == total:
            print("✅ РЕШЕНИЕ НАЙДЕНО!")
            print(f"   {num1:>15}")
            print(f"+  {num2:>15}")
            print(f"   {'-' * 15}")
            print(f"   {total:>15}")
            print("\n🔑 Расшифровка всех букв:")
            # Сортируем вывод для красоты
            for letter in sorted(current_map.keys()):
                print(f"   {letter} = {current_map[letter]}")
            return True

    print("\n❌ Решение не найдено при заданных условиях.")
    print("Попробуйте проверить ввод или изменить известные значения.")
    return False


if __name__ == "__main__":
    try:
        solve_crypto_arithmetic()
    except ValueError:
        print("\n❌ Ошибка ввода: Убедитесь, что вы вводите цифры правильно.")
    except KeyboardInterrupt:
        print("\n\nПрограмма остановлена пользователем.")