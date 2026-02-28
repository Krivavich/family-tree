# Family Tree — Release Candidate Plus

Продолжаем после MVP: в этой итерации закрыт следующий блок задач из roadmap — **JWT + refresh + 2FA, granular-policy по ролям, очередь превью медиа, предложенные правки, GEDCOM import/export (базовый)**.

## Новое в этой версии

## 1) JWT + Refresh + 2FA
- `POST /api/auth/token/` — первичная аутентификация и создание 2FA challenge.
- `POST /api/auth/2fa/verify/` — подтверждение кода и выдача `access/refresh`.
- `POST /api/auth/token/refresh/` — refresh JWT.
- Модель `TwoFactorCode` хранит одноразовые коды и срок действия.

> Сейчас код 2FA возвращается в ответе API (demo-mode). Для prod нужно отправлять по email/SMS/TOTP app.

## 2) Ролевая политика owner/editor/viewer
- `IsTreeMember` ограничивает доступ только участниками дерева.
- `HasTreeWriteRole` разрешает модификации только owner/editor, viewer — read only.

## 3) Медиа: готовность к S3/MinIO + фоновые задачи
- Настройки хранения через `USE_S3`, `AWS_*` env.
- Добавлен `preview_file` для `MediaAsset`.
- Добавлена celery-task `generate_media_preview` (MVP-stub).

## 4) Предложенные правки и конфликтный workflow
- Модель `ProposedChange` (pending/approved/rejected).
- API endpoint `/api/proposed-changes/` для подачи предложений.
- Базис для дальнейшей модерации владельцем дерева.

## 5) GEDCOM import/export
- `python manage.py export_gedcom <tree_id> --output tree.ged`
- `python manage.py import_gedcom <tree_id> <input.ged>`
- Экспорт полноценного шаблона GEDCOM + импорт MVP-парсером по именам.

---

## Быстрый запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Инфраструктура для локальной разработки:
```bash
docker compose up -d db redis minio
```

---

## Что дальше (следующий шаг после этой итерации)
1. Настоящий production 2FA (TOTP/email/SMS) + rate limits + device binding.
2. Применение `ProposedChange` как транзакционного merge-flow.
3. Реальная генерация preview (Pillow/ffmpeg) и антивирусный скан upload-файлов.
4. Полноценный GEDCOM parser (семьи, браки, источники, места).
5. Тесты: unit + integration + permission matrix.
