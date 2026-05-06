"""
Юнит-тесты для метода Calculation.get_quantity_for_product().

Согласно требованиям задания (Сессия 2):
    * 10 тестов низкой сложности — позитивные/негативные сценарии
                                    с очевидным ожидаемым результатом
    * 5 тестов высокой сложности  — точные расчёты, граничные значения,
                                    проверка алгоритма по эталону
"""

import unittest
import sys
import os

# чтобы тест работал при запуске из корня репозитория
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from WSUniversalLib import Calculation


class TestGetQuantityForProductSimple(unittest.TestCase):
    """10 тестов низкой сложности."""

    # 1
    def test_returns_int(self):
        """Метод должен возвращать int"""
        result = Calculation.get_quantity_for_product(1, 1, 10, 5.0, 5.0)
        self.assertIsInstance(result, int)

    # 2
    def test_non_existent_product_type(self):
        """Несуществующий тип продукции -> -1"""
        result = Calculation.get_quantity_for_product(99, 1, 10, 5.0, 5.0)
        self.assertEqual(result, -1)

    # 3
    def test_non_existent_material_type(self):
        """Несуществующий тип материала -> -1"""
        result = Calculation.get_quantity_for_product(1, 99, 10, 5.0, 5.0)
        self.assertEqual(result, -1)

    # 4
    def test_zero_count(self):
        """Нулевое количество продукции -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, 0, 5.0, 5.0)
        self.assertEqual(result, -1)

    # 5
    def test_negative_count(self):
        """Отрицательное количество -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, -10, 5.0, 5.0)
        self.assertEqual(result, -1)

    # 6
    def test_zero_width(self):
        """Нулевая ширина -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, 10, 0, 5.0)
        self.assertEqual(result, -1)

    # 7
    def test_negative_length(self):
        """Отрицательная длина -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, 10, 5.0, -5.0)
        self.assertEqual(result, -1)

    # 8
    def test_string_width(self):
        """Строка вместо float (ширина) -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, 10, "abc", 5.0)
        self.assertEqual(result, -1)

    # 9
    def test_float_count(self):
        """Дробное количество вместо int -> -1"""
        result = Calculation.get_quantity_for_product(1, 1, 10.5, 5.0, 5.0)
        self.assertEqual(result, -1)

    # 10
    def test_positive_result_for_valid_input(self):
        """При корректных входных данных результат должен быть положительным"""
        result = Calculation.get_quantity_for_product(1, 1, 10, 5.0, 5.0)
        self.assertGreater(result, 0)


class TestGetQuantityForProductComplex(unittest.TestCase):
    """5 тестов высокой сложности."""

    # 1 — эталонный пример из задания
    def test_reference_example_from_task(self):
        """
        Из ТЗ: 15 ед. продукции типа 3, размер 20x45, материал тип 1.
        Качественного сырья: 113 805. С учётом брака: 114 147,442 -> 114 148.
        """
        result = Calculation.get_quantity_for_product(3, 1, 15, 20, 45)
        self.assertEqual(result, 114148)

    # 2 — точная проверка коэффициента продукции типа 1 (1.1)
    def test_product_type_1_coefficient(self):
        """
        Тип 1 (1.1), материал тип 2 (брак 0.12%), 1 ед., 10x10
        100 * 1.1 = 110, /0.9988 = 110.13... -> 111
        """
        result = Calculation.get_quantity_for_product(1, 2, 1, 10, 10)
        self.assertEqual(result, 111)

    # 3 — точная проверка коэффициента продукции типа 2 (2.5)
    def test_product_type_2_coefficient(self):
        """
        Тип 2 (2.5), материал тип 1 (брак 0.3%), 4 ед., 5x5
        25 * 2.5 * 4 = 250, /0.997 = 250.752... -> 251
        """
        result = Calculation.get_quantity_for_product(2, 1, 4, 5, 5)
        self.assertEqual(result, 251)

    # 4 — крупные значения, разный тип материала
    def test_large_values_material_type_2(self):
        """
        Тип продукции 3 (8.43), материал тип 2 (брак 0.12%),
        100 ед., 30x60
        per_unit = 30*60*8.43 = 15174
        total = 15174 * 100 = 1517400
        / 0.9988 = 1519223.067... -> 1519224
        """
        result = Calculation.get_quantity_for_product(3, 2, 100, 30, 60)
        self.assertEqual(result, 1519224)

    # 5 — комбинированный негативный кейс: оба параметра невалидны
    def test_multiple_invalid_parameters(self):
        """Сразу несколько ошибок -> всё равно -1"""
        result = Calculation.get_quantity_for_product(99, 99, -1, 0, -10)
        self.assertEqual(result, -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
