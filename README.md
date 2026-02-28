# Family Tree — MVP старт на Django

Этот репозиторий теперь содержит **рабочий стартовый каркас** для вашего проекта семейного древа с API-first подходом:
- доменная схема (деревья, участники, персоны, связи, факты, версии фактов, медиа);
- REST API для персон и связей;
- минимальный web UI (CRUD для персон и создание связей);
- подготовка под PostgreSQL;
- аудит действий и версионирование фактов.

## Что уже реализовано

## 1) Доменная модель
- `Tree`, `TreeMembership` (roles: owner/editor/viewer)
- `Person`, `Relationship`
- `MediaAsset` (фото/документы)
- `Fact`, `FactVersion` (история изменений фактов)
- `AuditLog`

## 2) API и контракт
- DRF ViewSet для:
  - `GET/POST /api/persons/`
  - `GET/PATCH/DELETE /api/persons/{id}/`
  - `GET/POST /api/relationships/`
- Автосхема DRF: `/api/schema/`
- Зафиксированный OpenAPI-контракт: `docs/openapi.yaml`

## 3) Минимальный web UI
- список людей;
- создание/редактирование/удаление человека;
- список связей;
- создание связи.

## 4) Приватность и роли
- поле приватности в `Person`: `public | family | private`;
- роли в `TreeMembership`.

## 5) Готовность к PostgreSQL
- конфиг `docker-compose.yml` с Postgres;
- переключение SQLite/Postgres через `USE_SQLITE`.

---

## Быстрый запуск

1. Создайте и активируйте venv.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. (Опционально) Поднимите PostgreSQL:
   ```bash
   docker compose up -d db
   ```
4. Примените миграции:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Создайте администратора:
   ```bash
   python manage.py createsuperuser
   ```
6. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

---

## Следующий шаг (приоритет)
1. JWT-auth (login/refresh/logout + 2FA).
2. Политики доступа на уровне дерева/ветвей в API.
3. Upload в S3-совместимое хранилище + превью медиа.
4. Полноценный audit middleware (кто/что/когда).
5. Импорт/экспорт GEDCOM.
6. Механизм "предложить правку" и модерация конфликтов.
