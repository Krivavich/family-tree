# Family Tree — Security-hardened Release Candidate

Проведён критический security review проекта и исправлен ряд уязвимостей/рисков.

## Исправления безопасности и качества

1. **JWT/2FA hardening**
- Аутентификация теперь сначала проверяет `username/password` через `authenticate`, и только потом создаёт 2FA challenge.
- 2FA-коды больше не хранятся в plaintext: хранится HMAC-хэш (`code_hash`).
- Проверка кода выполняется через constant-time сравнение (`hmac.compare_digest`).
- Добавлен anti-spam лимит на выдачу нового 2FA challenge (не чаще 1 раза в 60 сек).
- Добавлен endpoint logout с blacklist refresh token: `POST /api/auth/logout/`.

2. **Django security defaults**
- `DEBUG=0` по умолчанию.
- Требование `DJANGO_SECRET_KEY` в non-debug окружении.
- `ALLOWED_HOSTS` по умолчанию ограничен localhost.
- Добавлены `CSRF_TRUSTED_ORIGINS`, secure-cookie/HSTS/SSL env-флаги.
- Включены password validators.
- Подключен `rest_framework_simplejwt.token_blacklist`.

3. **Runtime integrity improvements**
- `AuditUserMiddleware` теперь очищает контекст в `finally`, чтобы избежать утечек контекста между запросами при исключениях.
- В `Person` и `Relationship` вызов `full_clean()` перенесён в `save()`, чтобы валидации выполнялись не только через формы.

## API (актуально)
- `POST /api/auth/token/`
- `POST /api/auth/2fa/verify/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/logout/`
- `GET/POST /api/persons/`
- `GET/POST /api/relationships/`
- `GET/POST /api/proposed-changes/`

OpenAPI: `docs/openapi.yaml`.

## Важная пометка для production
Сейчас debug-код 2FA возвращается **только если `DEBUG=1`**. Для production нужно отправлять код через email/SMS/TOTP provider.
