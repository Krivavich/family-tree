param(
    [switch]$UseDocker
)

$ErrorActionPreference = 'Stop'

function Ensure-ProjectRoot {
    if (Test-Path -Path "manage.py" -PathType Leaf) {
        return
    }

    $nestedRepo = Join-Path (Get-Location) "family-tree"
    if (Test-Path -Path (Join-Path $nestedRepo "manage.py") -PathType Leaf) {
        Write-Warning "Похоже, вы запустили скрипт на уровень выше проекта. Перехожу в .\\family-tree"
        Set-Location $nestedRepo
        return
    }

    throw "Не найден manage.py. Запустите скрипт из корня проекта Family Tree."
}

Ensure-ProjectRoot

if (-not (Test-Path -Path ".env.example" -PathType Leaf)) {
    Write-Warning ".env.example не найден в текущем каталоге. Пытаюсь восстановить из git..."
    git checkout HEAD -- .env.example 2>$null
}

if (-not (Test-Path -Path ".env.example" -PathType Leaf)) {
    Write-Warning "Не удалось восстановить .env.example из git. Создаю минимальный .env."
@"
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000
DJANGO_SECURE_SSL_REDIRECT=0
DJANGO_SESSION_COOKIE_SECURE=0
DJANGO_CSRF_COOKIE_SECURE=0
DJANGO_CSRF_COOKIE_HTTPONLY=0
DJANGO_SECURE_REFERRER_POLICY=strict-origin-when-cross-origin
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=0
DJANGO_SECURE_HSTS_PRELOAD=0
POSTGRES_DB=family_tree
POSTGRES_USER=family_tree
POSTGRES_PASSWORD=family_tree
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
USE_SQLITE=1
USE_S3=0
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123
AWS_STORAGE_BUCKET_NAME=family-tree
AWS_S3_ENDPOINT_URL=http://localhost:9000
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"@ | Set-Content -Encoding UTF8 .env
} else {
    Copy-Item .env.example .env -Force
}

if ($UseDocker) {
    (Get-Content .env) -replace '^USE_SQLITE=1$', 'USE_SQLITE=0' | Set-Content .env
    docker compose up -d db redis minio
}

if (-not (Test-Path -Path ".venv" -PathType Container)) {
    python -m venv .venv
}

& .\.venv\Scripts\python -m pip install -r requirements.txt
& .\.venv\Scripts\python manage.py migrate
Write-Host "Готово. Запуск: .\.venv\Scripts\python manage.py runserver 127.0.0.1:8000"
