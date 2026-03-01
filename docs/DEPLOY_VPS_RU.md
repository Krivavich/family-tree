# Полная пошаговая инструкция деплоя на VPS (Ubuntu + Nginx + Gunicorn + PostgreSQL + Redis)

## 1. Базовая подготовка VPS
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx postgresql postgresql-contrib redis-server git
```

## 2. Создание системного пользователя
```bash
sudo adduser familytree
sudo usermod -aG sudo familytree
su - familytree
```

## 3. Клонирование проекта
```bash
git clone <REPO_URL> app
cd app
```

## 4. Виртуальное окружение и зависимости
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 5. PostgreSQL
```bash
sudo -u postgres psql
```
Внутри `psql`:
```sql
CREATE DATABASE family_tree;
CREATE USER family_tree_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE family_tree TO family_tree_user;
\q
```

## 6. Настройка `.env`
```bash
cp .env.example .env
```
Обновите значения:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=example.com,www.example.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com`
- `USE_SQLITE=0`
- `POSTGRES_DB=family_tree`
- `POSTGRES_USER=family_tree_user`
- `POSTGRES_PASSWORD=strong_password`
- `POSTGRES_HOST=127.0.0.1`

## 7. Миграции и статика
```bash
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 8. Gunicorn systemd unit
Создайте `/etc/systemd/system/familytree.service`:
```ini
[Unit]
Description=Family Tree Gunicorn
After=network.target

[Service]
User=familytree
Group=www-data
WorkingDirectory=/home/familytree/app
EnvironmentFile=/home/familytree/app/.env
ExecStart=/home/familytree/app/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable familytree
sudo systemctl start familytree
sudo systemctl status familytree
```

## 9. Nginx reverse proxy
Создайте `/etc/nginx/sites-available/familytree`:
```nginx
server {
    listen 80;
    server_name example.com www.example.com;

    location /static/ {
        alias /home/familytree/app/staticfiles/;
    }

    location /media/ {
        alias /home/familytree/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/familytree /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 10. HTTPS через Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

## 11. Celery worker (опционально)
Создайте unit `/etc/systemd/system/familytree-celery.service`:
```ini
[Unit]
Description=Family Tree Celery Worker
After=network.target redis.service

[Service]
User=familytree
Group=www-data
WorkingDirectory=/home/familytree/app
EnvironmentFile=/home/familytree/app/.env
ExecStart=/home/familytree/app/.venv/bin/celery -A config worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable familytree-celery
sudo systemctl start familytree-celery
```

## 12. Обновление приложения
```bash
cd /home/familytree/app
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart familytree
sudo systemctl restart familytree-celery
```

## 13. Чек-лист безопасности
- `DJANGO_DEBUG=0`
- сильный `DJANGO_SECRET_KEY`
- HTTPS включен
- резервные копии БД
- fail2ban / firewall
- ограничение доступа к SSH по ключам
