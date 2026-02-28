# Family Tree — Next Iteration (Security + Reliability + Liquid Glass UI)

В этой итерации проект усилен в трёх направлениях: безопасность, надёжность бизнес-логики и современный визуальный стиль Liquid Glass.

## Что сделано

### 1) Production-oriented 2FA + device binding
- Поддержаны устройства 2FA: `email`, `sms`, `totp` (`TwoFactorDevice`).
- Поддержаны доверенные устройства (`TrustedDevice`) с привязкой к `user-agent`/`ip` и TTL.
- Логин может пропускать 2FA только при валидном `trusted_device_token` и совпадении device fingerprint.
- Для TOTP добавлена встроенная верификация (без внешней зависимости).
- Для email/sms сохранён интеграционный hook `send_2fa_code`.
- Анти-спам выдачи challenge сохранён (60 секунд).

### 2) ProposedChange merge-flow
- Добавлен transactional apply/reject сервис.
- API actions:
  - `POST /api/proposed-changes/{id}/approve/`
  - `POST /api/proposed-changes/{id}/reject/`
- Одобрение owner-ом дерева применяет whitelisted поля в транзакции.

### 3) Media security + preview
- Добавлена server-side валидация загрузок:
  - лимит размера,
  - сигнатура EICAR (базовый AV guard).
- `MediaAsset` валидируется на `save()`.
- `generate_media_preview` генерирует JPG preview через Pillow (fallback-safe).

### 4) GEDCOM parser улучшен
- Импорт парсит `INDI`, `NAME`, `BIRT/DEAT DATE`, `FAM`, `HUSB/CHIL`.
- Создаются `Person` и parent-child `Relationship` при импорте.

### 5) Тестирование
- Добавлены unit/integration tests для:
  - 2FA hashing/TOTP/trusted-device механики,
  - merge-flow предложенных правок,
  - media validation.

### 6) UI / Design
- Полностью обновлён base-стиль в формате **Liquid Glass**:
  - градиентный фон,
  - стеклянные карточки (`backdrop-filter`),
  - «жидкие» скруглённые элементы,
  - glow/blob-акценты и улучшенная визуальная иерархия.

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
