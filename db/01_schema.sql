-- Схема БД для подсистемы работы с материалами
-- При повторном запуске сначала чистим всё (порядок важен из-за FK)
DROP TABLE IF EXISTS product_material   CASCADE;
DROP TABLE IF EXISTS material_supplier  CASCADE;
DROP TABLE IF EXISTS material           CASCADE;
DROP TABLE IF EXISTS supplier           CASCADE;
DROP TABLE IF EXISTS product            CASCADE;
DROP TABLE IF EXISTS material_type      CASCADE;
DROP TABLE IF EXISTS supplier_type      CASCADE;
DROP TABLE IF EXISTS product_type       CASCADE;


-- Справочники
-- Тип материала (Гранулы, Краски, Нитки и т.п.)
-- defect_percent — процент брака для расчёта в библиотеке (0.3% / 0.12%)
CREATE TABLE material_type (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    defect_percent  NUMERIC(5,2) NOT NULL DEFAULT 0
        CHECK (defect_percent >= 0)
);

-- Тип поставщика (ООО, ОАО, ЗАО, ПАО, МКК, МФО, ИП и т.д.)
CREATE TABLE supplier_type (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(50) NOT NULL UNIQUE
);

-- Тип продукции (для коэффициента в расчёте сырья)
CREATE TABLE product_type (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) NOT NULL UNIQUE,
    coefficient   NUMERIC(6,3) NOT NULL CHECK (coefficient > 0)
);


-- Основные сущности

-- Материал (сырьё)
CREATE TABLE material (
    id                 SERIAL PRIMARY KEY,
    name               VARCHAR(200) NOT NULL,
    material_type_id   INT NOT NULL REFERENCES material_type(id) ON DELETE RESTRICT,
    image_path         VARCHAR(255),                       -- путь к картинке, NULL = заглушка
    price              NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    stock_quantity     INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    min_quantity       INT NOT NULL DEFAULT 0 CHECK (min_quantity >= 0),
    package_quantity   INT NOT NULL DEFAULT 1 CHECK (package_quantity > 0),
    unit               VARCHAR(20) NOT NULL,               -- л, кг, г, м и пр.
    description        TEXT
);

-- Поставщик
CREATE TABLE supplier (
    id                 SERIAL PRIMARY KEY,
    name               VARCHAR(200) NOT NULL,
    supplier_type_id   INT NOT NULL REFERENCES supplier_type(id) ON DELETE RESTRICT,
    inn                VARCHAR(12)  NOT NULL UNIQUE,
    quality_rating     INT          CHECK (quality_rating BETWEEN 0 AND 100),
    start_date         DATE
);

-- Продукция (минимальная таблица — нужна, чтобы запретить удаление
-- материалов, которые используются в производстве)
CREATE TABLE product (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(200) NOT NULL,
    product_type_id INT NOT NULL REFERENCES product_type(id) ON DELETE RESTRICT,
    article         VARCHAR(50) UNIQUE,
    min_price       NUMERIC(12,2) CHECK (min_price >= 0)
);


-- Связи M:N

-- Поставщики материала (один материал — много поставщиков, и наоборот)
CREATE TABLE material_supplier (
    material_id  INT NOT NULL REFERENCES material(id) ON DELETE CASCADE,
    supplier_id  INT NOT NULL REFERENCES supplier(id) ON DELETE CASCADE,
    PRIMARY KEY (material_id, supplier_id)
);

-- Используемые в продукции материалы
-- ON DELETE RESTRICT — нельзя удалить материал, если он есть в продукции
CREATE TABLE product_material (
    product_id   INT NOT NULL REFERENCES product(id)  ON DELETE CASCADE,
    material_id  INT NOT NULL REFERENCES material(id) ON DELETE RESTRICT,
    quantity     NUMERIC(12,3) NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (product_id, material_id)
);


-- Индексы для ускорения поиска/сортировки в приложении
CREATE INDEX idx_material_name          ON material (name);
CREATE INDEX idx_material_type_id       ON material (material_type_id);
CREATE INDEX idx_supplier_name          ON supplier (name);
