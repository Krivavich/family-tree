# Family Tree — Release Candidate (Django MVP)

Это уже не просто каркас: проект приведён к состоянию **release-candidate для MVP**, с фокусом на безопасность доступа, качество данных и расширяемость.

## Что улучшено критически

1. **Контроль доступа по членству в дереве**
   - Web UI показывает только данные деревьев пользователя.
   - API фильтрует queryset по `TreeMembership`.
   - Object-level permission в API запрещает доступ к чужим деревьям.

2. **Целостность генеалогических данных**
   - Проверка дат (`death_date` не раньше `birth_date`).
   - Запрет самоссылок в связях (`no_self_relationship`).
   - Уникальность связи в пределах дерева.
   - Уникальность ключа факта в пределах человека.

3. **Версионирование фактов без дублей**
   - История фактов (`FactVersion`) создаётся через сигнал.
   - Новая версия добавляется только при реальном изменении содержимого.

4. **Аудит действий (create/update/delete)**
   - Middleware сохраняет текущего пользователя в контекст запроса.
   - Сигналы пишут `AuditLog` для `Person`, `Relationship`, `Fact`.

5. **Современный UI-слой и UX**
   - Новый тёмный modern-style интерфейс.
   - Добавлен login flow (`/accounts/login/`) и logout в шапке.
   - Улучшены формы и навигация.

6. **Готовность к деплою и миграциям**
   - Добавлены initial migrations для `users`, `genealogy`, `audit`.
   - Сохранены `.env.example`, `docker-compose.yml`, OpenAPI контракт.

---

## Архитектура
- Backend: Django + DRF
- DB: SQLite (локально) / PostgreSQL (prod-ready)
- Apps:
  - `apps.users` — кастомный пользователь
  - `apps.genealogy` — деревья, персоны, связи, факты, медиа
  - `apps.audit` — журнал действий

---

## API
- `GET/POST /api/persons/`
- `GET/PATCH/DELETE /api/persons/{id}/`
- `GET/POST /api/relationships/`
- `GET /api/schema/`
- Контракт: `docs/openapi.yaml`

---

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

PostgreSQL (опционально):
```bash
docker compose up -d db
```

---

## Что в ближайший релиз после MVP
1. JWT + refresh + 2FA.
2. Роли owner/editor/viewer на уровне эндпоинтов с granular-policy.
3. Загрузка медиа в S3/MinIO + генерация preview (Celery).
4. Предложенные правки + разрешение конфликтов данных.
5. Импорт/экспорт GEDCOM.
