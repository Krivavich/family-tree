# Требования к инфраструктуре (Hosting/VPS)

## 1. Минимум (MVP, до ~300 активных пользователей)

### Shared Hosting / Managed
- Python 3.11+
- WSGI поддержка
- PostgreSQL 13+
- RAM: от 1 GB
- CPU: 1 vCPU
- Диск: 10 GB SSD
- SSL сертификат

### VPS
- 1 vCPU
- 2 GB RAM
- 20 GB SSD
- Ubuntu 22.04+
- PostgreSQL + Redis

---

## 2. Норма (рабочий прод, ~300–3000 пользователей)

### VPS / Cloud VM
- 2–4 vCPU
- 4–8 GB RAM
- 60+ GB SSD
- PostgreSQL отдельным инстансом или managed DB
- Redis для cache/queue
- Object Storage (S3/MinIO) для медиа
- Бэкапы: daily full + binlog/WAL strategy

---

## 3. Максимум (рост, 3000+ пользователей, heavy media)

### Production cluster
- App nodes: 2+ (каждый 4–8 vCPU, 8–16 GB RAM)
- DB node: 8+ vCPU, 16+ GB RAM, NVMe
- Redis HA
- S3-compatible object storage / CDN
- Nginx + WAF
- Observability: metrics/logging/tracing
- CI/CD + blue/green или rolling deployment

---

## 4. Сетевые и эксплуатационные требования
- HTTPS only
- Автообновление TLS сертификатов
- Firewall (только нужные порты)
- Регулярные security updates
- Мониторинг ошибок и latency

---

## 5. Рекомендации по выбору
- Для старта: 2 vCPU / 4 GB RAM VPS.
- Для стабильного роста: 4 vCPU / 8 GB RAM + managed PostgreSQL.
- Для медиа-нагрузки: отдельное object storage + CDN + очереди Celery workers.
