-- ============================================================
-- База данных проекта demoexam_26
-- Демоэкзамен 09.02.07, уровень ПУ
-- Стек: Django + PostgreSQL
-- ============================================================

-- В этом файле показаны основные таблицы предметной области.
-- Служебные таблицы Django auth_*, django_* и таблицы прав не включены,
-- потому что для ER-диаграммы и защиты обычно нужны именно таблицы проекта.


-- ============================================================
-- Удаление таблиц, если файл запускается повторно
-- ============================================================

DROP TABLE IF EXISTS core_orderitem CASCADE;
DROP TABLE IF EXISTS core_order CASCADE;
DROP TABLE IF EXISTS core_product CASCADE;
DROP TABLE IF EXISTS core_user CASCADE;
DROP TABLE IF EXISTS core_pickuppoint CASCADE;
DROP TABLE IF EXISTS core_supplier CASCADE;
DROP TABLE IF EXISTS core_manufacturer CASCADE;
DROP TABLE IF EXISTS core_category CASCADE;
DROP TABLE IF EXISTS core_role CASCADE;


-- ============================================================
-- Роли пользователей
-- ============================================================

CREATE TABLE core_role (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL UNIQUE
);


-- ============================================================
-- Пользователи системы
-- Таблица наследует основные поля Django-пользователя:
-- username, password, email, is_staff, is_active и др.
-- ============================================================

CREATE TABLE core_user (
    id           BIGSERIAL PRIMARY KEY,
    password     VARCHAR(128) NOT NULL,
    last_login   TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username     VARCHAR(150) NOT NULL UNIQUE,
    first_name   VARCHAR(150) NOT NULL DEFAULT '',
    last_name    VARCHAR(150) NOT NULL DEFAULT '',
    email        VARCHAR(254) NOT NULL DEFAULT '',
    is_staff     BOOLEAN NOT NULL DEFAULT FALSE,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    full_name    VARCHAR(255) NOT NULL,
    role_id      BIGINT REFERENCES core_role(id) ON DELETE SET NULL
);


-- ============================================================
-- Категории товаров
-- ============================================================

CREATE TABLE core_category (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);


-- ============================================================
-- Производители
-- ============================================================

CREATE TABLE core_manufacturer (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);


-- ============================================================
-- Поставщики
-- ============================================================

CREATE TABLE core_supplier (
    id   BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE
);


-- ============================================================
-- Пункты выдачи
-- ============================================================

CREATE TABLE core_pickuppoint (
    id      BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL UNIQUE
);


-- ============================================================
-- Товары
-- ============================================================

CREATE TABLE core_product (
    id              BIGSERIAL PRIMARY KEY,
    article         VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    unit            VARCHAR(20) NOT NULL DEFAULT 'шт.',
    price           NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    supplier_id     BIGINT NOT NULL REFERENCES core_supplier(id) ON DELETE RESTRICT,
    manufacturer_id BIGINT NOT NULL REFERENCES core_manufacturer(id) ON DELETE RESTRICT,
    category_id     BIGINT NOT NULL REFERENCES core_category(id) ON DELETE RESTRICT,
    discount        NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (discount >= 0 AND discount <= 100),
    quantity        INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    description     TEXT NOT NULL DEFAULT '',
    photo           VARCHAR(100)
);


-- ============================================================
-- Заказы
-- ============================================================

CREATE TABLE core_order (
    id              BIGSERIAL PRIMARY KEY,
    order_date      DATE NOT NULL,
    delivery_date   DATE NOT NULL,
    pickup_point_id BIGINT NOT NULL REFERENCES core_pickuppoint(id) ON DELETE RESTRICT,
    client_id       BIGINT REFERENCES core_user(id) ON DELETE SET NULL,
    client_name     VARCHAR(255) NOT NULL DEFAULT '',
    pickup_code     INTEGER NOT NULL DEFAULT 0 CHECK (pickup_code >= 0),
    status          VARCHAR(30) NOT NULL DEFAULT 'new'
);


-- ============================================================
-- Позиции заказа
-- Один заказ может содержать несколько товаров.
-- Товар нельзя удалить, если он присутствует в заказе.
-- ============================================================

CREATE TABLE core_orderitem (
    id         BIGSERIAL PRIMARY KEY,
    order_id   BIGINT NOT NULL REFERENCES core_order(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES core_product(id) ON DELETE RESTRICT,
    count      INTEGER NOT NULL DEFAULT 1 CHECK (count > 0)
);


-- ============================================================
-- Начальные данные: роли
-- Гость в базе не хранится: гость = неавторизованный пользователь.
-- ============================================================

INSERT INTO core_role (name)
VALUES
    ('admin'),
    ('manager'),
    ('client');


-- ============================================================
-- Тестовые пользователи
-- Пароль у всех тестовых пользователей: 123456
-- Пароли записаны как Django-хэши, а не обычным текстом.
-- ============================================================

INSERT INTO core_user (
    username,
    password,
    full_name,
    first_name,
    last_name,
    email,
    is_superuser,
    is_staff,
    is_active,
    role_id
)
VALUES (
    'admin',
    'pbkdf2_sha256$1000000$gFKMUOxJm4Tpy2AzTmtzW6$Sm3P3ftV0YMoLmTcEDRH14IF2XmkIU7ydfsqp76AaM0=',
    'Иванов Иван Иванович',
    'Иван',
    'Иванов',
    'admin@example.local',
    TRUE,
    TRUE,
    TRUE,
    (SELECT id FROM core_role WHERE name = 'admin')
);

INSERT INTO core_user (
    username,
    password,
    full_name,
    first_name,
    last_name,
    email,
    is_superuser,
    is_staff,
    is_active,
    role_id
)
VALUES (
    'manager',
    'pbkdf2_sha256$1000000$IzIhmPvLT6ydFulnDnWkA1$8bgu7aWGRyvv25pN5S6MLEZOyvHyzoKvHeP6DAUqjtU=',
    'Петров Петр Петрович',
    'Петр',
    'Петров',
    'manager@example.local',
    FALSE,
    FALSE,
    TRUE,
    (SELECT id FROM core_role WHERE name = 'manager')
);

INSERT INTO core_user (
    username,
    password,
    full_name,
    first_name,
    last_name,
    email,
    is_superuser,
    is_staff,
    is_active,
    role_id
)
VALUES (
    'client',
    'pbkdf2_sha256$1000000$gwLRiJGZtx9RZVdh39Iy8h$ZiaQBEEAE+cnfDhs15Z/tZzgziWFHgRidnJg4txyiN0=',
    'Сидоров Сидор Сидорович',
    'Сидор',
    'Сидоров',
    'client@example.local',
    FALSE,
    FALSE,
    TRUE,
    (SELECT id FROM core_role WHERE name = 'client')
);


-- ============================================================
-- Минимальные справочные данные для проверки
-- ============================================================

INSERT INTO core_category (name)
VALUES ('Обувь');

INSERT INTO core_manufacturer (name)
VALUES ('Не указан');

INSERT INTO core_supplier (name)
VALUES ('Основной поставщик');

INSERT INTO core_pickuppoint (address)
VALUES ('г. Москва, ул. Примерная, д. 1');


-- ============================================================
-- Тестовый товар
-- ============================================================

INSERT INTO core_product (
    article,
    name,
    unit,
    price,
    supplier_id,
    manufacturer_id,
    category_id,
    discount,
    quantity,
    description,
    photo
)
VALUES (
    'TEST-001',
    'Тестовый товар',
    'шт.',
    1000.00,
    (SELECT id FROM core_supplier WHERE name = 'Основной поставщик'),
    (SELECT id FROM core_manufacturer WHERE name = 'Не указан'),
    (SELECT id FROM core_category WHERE name = 'Обувь'),
    10.00,
    5,
    'Товар для проверки работы базы данных.',
    NULL
);


-- ============================================================
-- Тестовый заказ
-- ============================================================

INSERT INTO core_order (
    order_date,
    delivery_date,
    pickup_point_id,
    client_id,
    client_name,
    pickup_code,
    status
)
VALUES (
    CURRENT_DATE,
    CURRENT_DATE + 3,
    (SELECT id FROM core_pickuppoint LIMIT 1),
    (SELECT id FROM core_user WHERE username = 'client'),
    'Сидоров Сидор Сидорович',
    123,
    'new'
);

INSERT INTO core_orderitem (
    order_id,
    product_id,
    count
)
VALUES (
    (SELECT id FROM core_order ORDER BY id DESC LIMIT 1),
    (SELECT id FROM core_product WHERE article = 'TEST-001'),
    1
);


-- ============================================================
-- Проверочные SELECT-запросы
-- ============================================================

SELECT * FROM core_role;
SELECT * FROM core_user;
SELECT * FROM core_product;
SELECT * FROM core_order;
SELECT * FROM core_orderitem;
