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
- Browsable API отключён по умолчанию, чтобы пользователи не попадали на DRF HTML-формы вместо web UI; для включения выставьте `DJANGO_ENABLE_BROWSABLE_API=1`.
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
- Исправлен блокирующий UX-баг формы персоны: для нового пользователя без деревьев автоматически создаётся персональное дерево, чтобы поле `Tree` не было пустым.
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


## 11. Как запустить из локального репозитория (Windows + Docker)

Локальная папка из вашего примера: `C:\Projects\family-tree`.

### 11.1 Проверка Docker и переход в репозиторий (PowerShell)
```powershell
cd C:\Projects\family-tree
docker --version
docker compose version
```

### 11.2 Создание `.env` (обязательно)
```powershell
Copy-Item .env.example .env
```

> Начиная с этой ревизии, `config/settings.py` автоматически подхватывает `.env` через `config/env.py`.

### 11.2.1 Если PowerShell пишет, что `.env.example` не существует

Ошибка вида:
`Copy-Item : Не удается найти путь ... .env.example`

Проверьте и исправьте так:

```powershell
cd C:\Projects\family-tree
git status
```

Если видите `No commits yet` и `Untracked files: family-tree/`, вы находитесь **на уровень выше** реального проекта.

Перейдите в вложенную папку и повторите:

```powershell
cd .\family-tree
Test-Path .env.example
Copy-Item .env.example .env
```

Если вы уже в правильной папке, но файла нет:

```powershell
# восстановить файл из текущего коммита (если случайно удалили локально)
git checkout HEAD -- .env.example

# снова создать .env
Copy-Item .env.example .env
```

Если `git checkout HEAD -- .env.example` падает с `invalid reference: HEAD`, это неинициализированная/пустая папка, а не ваш репозиторий — нужно перейти в папку, где есть `manage.py` и история git.

Альтернатива: используйте автоматический скрипт `scripts/setup-local.ps1`, который сам проверяет, что вы в корне проекта, и при необходимости автоматически переходит в `.\family-tree`.

```powershell
cd C:\Projects\family-tree
powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1
```

Для режима с Docker-инфрой:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1 -UseDocker
```


Если при запуске `setup-local.ps1` видите ошибку `TerminatorExpectedAtEndOfString`, обновите репозиторий до последнего коммита и запустите скрипт снова:

```powershell
cd C:\Projects\family-tree\family-tree
git pull
powershell -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1
```

### 11.3 Вариант A: быстрый локальный старт на SQLite (без контейнеров)
```powershell
cd C:\Projects\family-tree
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

### 11.4 Вариант B: локальный старт с Docker-инфрой (PostgreSQL + Redis + MinIO)
```powershell
cd C:\Projects\family-tree
Copy-Item .env.example .env

# переключаемся на PostgreSQL
(Get-Content .env) -replace '^USE_SQLITE=1$', 'USE_SQLITE=0' |
  Set-Content .env
(Get-Content .env) -replace '^POSTGRES_HOST=localhost$', 'POSTGRES_HOST=127.0.0.1' |
  Set-Content .env

# запускаем инфраструктуру
docker compose up -d db redis minio

# запускаем Django локально
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

Открыть в браузере:
- Приложение: `http://127.0.0.1:8000/`
- MinIO Console: `http://127.0.0.1:9001/` (логин/пароль `minio` / `minio123`)

### 11.5 Копирование проекта на удалённый Linux-сервер (если нужно)
```bash
git clone <YOUR_REPO_URL> family-tree
cd family-tree
rsync -avz --delete ./ user@YOUR_SERVER_IP:/opt/family-tree/
ssh user@YOUR_SERVER_IP
cd /opt/family-tree
```

## 12. Что исправлено в ревизии безопасности
- Убран сценарий user-enumeration в 2FA verify: для несуществующего пользователя теперь возвращается унифицированная ошибка.
- Для CRUD-форм (Person/Relationship/Event) добавлено ограничение по ролям: `viewer` не получает write-наборы данных.
- Для API событий добавлена проверка write-ролей (`owner/editor`) при create/update.
- Добавлены дополнительные security-настройки: `SECURE_REFERRER_POLICY`, `SESSION_COOKIE_HTTPONLY`, опциональный `CSRF_COOKIE_HTTPONLY`.


## 13. Автор и copyright
© Krivavich — GitHub: https://github.com/Krivavich
