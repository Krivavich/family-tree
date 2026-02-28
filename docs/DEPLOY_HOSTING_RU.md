# Пошаговый деплой на хостинг (shared hosting / managed hosting)

> Важно: не каждый shared hosting поддерживает Python/Django корректно. Предпочтительно использовать managed hosting с WSGI и PostgreSQL.

## 1. Подготовка
1. Получите доступы к хостингу: SSH/панель, БД, домен.
2. Создайте PostgreSQL базу и пользователя.
3. Настройте домен и SSL-сертификат.

## 2. Загрузка кода
1. Загрузите проект через git/архив.
2. Перейдите в директорию проекта.

## 3. Виртуальное окружение
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 4. Переменные окружения
Создайте `.env`:
- `DJANGO_SECRET_KEY=<strong-secret>`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com`
- `POSTGRES_*` (хост, порт, БД, пользователь, пароль)
- `USE_SQLITE=0`

## 5. Миграции и статика
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 6. WSGI/Panel setup
1. В панели хостинга укажите WSGI entrypoint на `config/wsgi.py`.
2. Пропишите путь к виртуальному окружению.
3. Перезапустите приложение из панели.

## 7. Проверка
1. Откройте сайт.
2. Проверьте `/admin`.
3. Проверьте логин/2FA и базовые CRUD операции.

## 8. Постдеплой
- Включите ротацию логов.
- Настройте резервные копии БД.
- Ограничьте доступ в админку (IP allowlist/2FA).
