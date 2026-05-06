"""
Класс расчёта количества сырья для производства продукции.

Спецификация (см. "Спецификация метода.pdf"):
    Название класса:    Calculation
    Название метода:    get_quantity_for_product()
    Параметры:
        product_type:  int   — идентификатор типа продукции (1, 2, 3)
        material_type: int   — идентификатор типа материала  (1, 2)
        count:         int   — количество необходимой продукции
        width:         float — ширина продукции
        length:        float — длина продукции
    Возвращает: int — количество сырья с учётом возможного брака,
                либо -1 при некорректных параметрах.
"""

import math


class Calculation:
    """Класс с расчётными методами производства."""

    # Коэффициенты типа продукции
    _PRODUCT_COEFFICIENTS = {
        1: 1.1,
        2: 2.5,
        3: 8.43,
    }

    # Процент брака для типа материала (в долях, не процентах)
    _MATERIAL_DEFECT_RATE = {
        1: 0.003,    # 0.3 %
        2: 0.0012,   # 0.12 %
    }

    @staticmethod
    def get_quantity_for_product(
        product_type: int,
        material_type: int,
        count: int,
        width: float,
        length: float,
    ) -> int:
        """
        Рассчитывает целое количество сырья, необходимого для производства
        :param product_type:   идентификатор типа продукции
        :param material_type:  идентификатор типа материала
        :param count:          количество единиц продукции
        :param width:          ширина продукции
        :param length:         длина продукции
        :return:               количество сырья (округлённое вверх) или -1 при ошибке
        """

        # --- валидация типов ---
        if not isinstance(product_type, int) or not isinstance(material_type, int):
            return -1
        if not isinstance(count, int):
            return -1
        if not isinstance(width, (int, float)) or not isinstance(length, (int, float)):
            return -1
        # bool — наследник int; явно отсекаем
        if isinstance(product_type, bool) or isinstance(material_type, bool) or isinstance(count, bool):
            return -1

        # --- валидация значений ---
        if product_type not in Calculation._PRODUCT_COEFFICIENTS:
            return -1
        if material_type not in Calculation._MATERIAL_DEFECT_RATE:
            return -1
        if count <= 0 or width <= 0 or length <= 0:
            return -1

        # --- сам расчёт ---
        product_coef = Calculation._PRODUCT_COEFFICIENTS[product_type]
        defect_rate  = Calculation._MATERIAL_DEFECT_RATE[material_type]

        # Сырья на единицу продукции = площадь * коэффициент типа
        per_unit = width * length * product_coef
        # Качественного сырья на всю партию
        total_quality = per_unit * count
        # С учётом брака: total / (1 - defect_rate) — компенсируем потери
        total_with_defect = total_quality / (1 - defect_rate)

        # Округление вверх до ближайшего большего целого
        return math.ceil(total_with_defect)
