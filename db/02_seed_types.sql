-- Заполнение справочников начальными значениями

INSERT INTO material_type (name, defect_percent) VALUES
    ('Тип материала 1', 0.30),
    ('Тип материала 2', 0.12),
    ('Гранулы',         0.30),
    ('Нитки',           0.12),
    ('Краски',          0.30)
ON CONFLICT (name) DO NOTHING;

INSERT INTO supplier_type (name) VALUES
    ('ООО'), ('ОАО'), ('ЗАО'), ('ПАО'),
    ('МКК'), ('МФО'), ('ИП'),  ('Самозанятый')
ON CONFLICT (name) DO NOTHING;

INSERT INTO product_type (name, coefficient) VALUES
    ('Тип продукции 1', 1.100),
    ('Тип продукции 2', 2.500),
    ('Тип продукции 3', 8.430)
ON CONFLICT (name) DO NOTHING;
