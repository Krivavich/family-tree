# Family Tree — Next Iteration (Security + Reliability)

В этой итерации проект продвинут по следующим направлениям: production-ready 2FA, device binding, транзакционный merge-flow предложенных правок, усиленная защита медиа-загрузок, улучшенный GEDCOM импорт и базовые тесты.

## Что сделано

### 1) Production-oriented 2FA
- Поддержаны устройства 2FA: `email`, `sms`, `totp` (`TwoFactorDevice`).
- Поддержаны доверенные устройства (`TrustedDevice`) с токеном на 30 дней.
- Логин может пропускать 2FA только при валидном `trusted_device_token`.
- Для TOTP добавлена верификация RFC6238-like (без внешней зависимости).
- Для email/sms оставлен интеграционный hook `send_2fa_code`.
- Анти-спам выдачи challenge сохранён (60 секунд).

### 2) ProposedChange merge-flow
- Добавлен transactional apply/reject сервис.
- API actions:
  - `POST /api/proposed-changes/{id}/approve/`
  - `POST /api/proposed-changes/{id}/reject/`
- Одобрение правки owner-ом дерева применяет изменения к целевой сущности в транзакции.

### 3) Media security + preview
- Добавлена server-side валидация загрузок:
  - лимит размера,
  - сигнатура EICAR (базовый AV guard).
- `MediaAsset` валидируется на `save()`.
- `generate_media_preview` теперь пытается генерировать JPG preview через Pillow (fallback-safe).

### 4) GEDCOM parser улучшен
- Импорт now parses `INDI`, `NAME`, `BIRT/DEAT DATE`, `FAM`, `HUSB/CHIL`.
- Создаются `Person` и parent-child `Relationship` при импорте.

### 5) Тестирование
- Добавлены unit/integration tests для:
  - 2FA hashing/TOTP/trusted-device механики,
  - permission matrix,
  - merge-flow предложенных правок,
  - media validation.

## Запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Инфраструктура dev
```bash
docker compose up -d db redis minio
```
