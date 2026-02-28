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
