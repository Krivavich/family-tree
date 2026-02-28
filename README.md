# Family Tree Platform — Developer README

Этот документ предназначен для разработчиков проекта Family Tree.

## 1. Что это за проект

Family Tree — web-платформа для совместного построения генеалогического древа:
- пользователи создают деревья;
- приглашают родственников;
- добавляют персон, связи, факты, медиа;
- предлагают правки и согласовывают их;
- используют API-first архитектуру для web/mobile клиентов.

Технологии ядра:
- Python + Django
- Django REST Framework
- PostgreSQL / SQLite (dev)
- JWT + 2FA
- Celery + Redis
- S3/MinIO (опционально)

---

## 2. Структура репозитория

- `apps/users` — кастомная модель пользователя.
- `apps/authentication` — 2FA, trusted devices, auth API.
- `apps/genealogy` — бизнес-домен (Tree/Person/Relationship/Fact/Media/ProposedChange).
- `apps/audit` — audit log и middleware/signals.
- `config` — настройки Django, роутинг, WSGI/ASGI.
- `templates` — web-интерфейс (Liquid Glass UI).
- `docs` — пользовательская, техническая и эксплуатационная документация.

---

## 3. Быстрый старт для разработчика

### 3.1 Локально (SQLite)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3.2 Локально (PostgreSQL + Redis + MinIO)
```bash
docker compose up -d db redis minio
python manage.py migrate
python manage.py runserver
```

---

## 4. Команды разработки

```bash
python manage.py runserver
python manage.py migrate
python manage.py test
python manage.py test apps.authentication apps.genealogy
python manage.py export_gedcom <tree_id> --output tree.ged
python manage.py import_gedcom <tree_id> <input.ged>
```

---

## 5. Важные переменные окружения

Смотрите `.env.example`. Ключевые:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `POSTGRES_*`
- `USE_SQLITE`
- `USE_S3`, `AWS_*`
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`

---

## 6. Безопасность (для разработчика)

- Не храните секреты в git.
- Для production выставляйте `DJANGO_DEBUG=0`.
- Настройте HTTPS, secure cookies, HSTS.
- Используйте реальные провайдеры 2FA каналов (email/SMS/TOTP app).
- Перед релизом выполняйте миграции и тесты.

---

## 7. Документация в папке `docs`

- `docs/USER_HELP_RU.md` — инструкция для пользователя.
- `docs/GENEALOGY_MAP_LOGIC_RU.md` — логика генеалогической модели.
- `docs/DEPLOY_HOSTING_RU.md` — пошаговый деплой на shared hosting.
- `docs/DEPLOY_VPS_RU.md` — пошаговый production деплой на VPS.
- `docs/INFRA_REQUIREMENTS_RU.md` — требования к инфраструктуре.
- `docs/PROJECT_REVIEW_RU.md` — критическая ревизия проекта и список спорных решений.


## 8. Что улучшено в последней ревизии
- Добавлен генеалогический таймлайн событий (`Event`) и API `/api/events/`.
- Добавлен индикатор полноты профиля персоны (подсказки для заполнения пробелов).
- Усилен auth-flow: scoped throttling + строгий verify через `challenge_id` для non-TOTP.
- Улучшена модерация правок: симметричная транзакционная reject-операция.
- Обновлён UI-набор: навигация по таймлайну, современная glass-стилистика.


## 9. Взгляд со стороны: что улучшено для привлекательности продукта
- Для пользователя: добавлен **семейный таймлайн событий**, который делает историю рода «живой», а не только графом связей.
- Для генеалога: добавлены поля `source_reference` в событиях и индикатор полноты профиля (где данные неполные).
- Для современного web UX: обновлена навигация под быстрые сценарии (люди / связи / таймлайн / добавить событие) и усилена liquid-glass визуальная иерархия.

## 10. Честная критика спорных решений
- 2FA канал email/SMS пока интеграционный stub; в production требуется подключение реального провайдера и SLA мониторинга доставки.
- GEDCOM импорт/экспорт пока базовый; для профессиональной генеалогии нужен расширенный парсер источников/семей/браков.
- Media AV-проверка базовая (EICAR); нужен полноценный внешнй антивирусный контур в асинхронном pipeline.


## 11. Как скопировать проект на локальный сервер и запустить локально

### 11.1 Копирование проекта на свой локальный сервер (Linux/macOS)
```bash
# 1) на локальном ПК
git clone <YOUR_REPO_URL> family-tree
cd family-tree

# 2) копирование на удалённый сервер (пример через rsync)
rsync -avz --delete ./ user@YOUR_SERVER_IP:/opt/family-tree/

# 3) подключение к серверу
ssh user@YOUR_SERVER_IP
cd /opt/family-tree
```

### 11.2 Запуск проекта для тестирования на локальном компьютере
```bash
# 1) подготовка
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 2) миграции и админ
python manage.py migrate
python manage.py createsuperuser

# 3) запуск
python manage.py runserver 0.0.0.0:8000
```

Открыть в браузере: `http://127.0.0.1:8000/`

### 11.3 Запуск локально через Docker (PostgreSQL + Redis + MinIO)
```bash
docker compose up -d db redis minio
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 12. Что исправлено в ревизии безопасности
- Убран сценарий user-enumeration в 2FA verify: для несуществующего пользователя теперь возвращается унифицированная ошибка.
- Для CRUD-форм (Person/Relationship/Event) добавлено ограничение по ролям: `viewer` не получает write-наборы данных.
- Для API событий добавлена проверка write-ролей (`owner/editor`) при create/update.
- Добавлены дополнительные security-настройки: `SECURE_REFERRER_POLICY`, `SESSION_COOKIE_HTTPONLY`, опциональный `CSRF_COOKIE_HTTPONLY`.


## 13. Автор и copyright
© Krivavich — GitHub: https://github.com/Krivavich
