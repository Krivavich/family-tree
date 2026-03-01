from pathlib import Path

from django.conf import settings

try:
    from celery import shared_task
except Exception:  # pragma: no cover
    def shared_task(func=None, **kwargs):
        def decorator(f):
            return f

        return decorator(func) if func else decorator


@shared_task
def generate_media_preview(media_asset_id: int) -> str:
    from .models import MediaAsset

    media = MediaAsset.objects.filter(id=media_asset_id).first()
    if not media:
        return f"media-not-found:{media_asset_id}"

    try:
        from PIL import Image

        media.file.open("rb")
        img = Image.open(media.file)
        img.thumbnail((512, 512))

        preview_dir = Path(settings.MEDIA_ROOT) / "media_previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        preview_name = f"preview_{media.id}.jpg"
        preview_path = preview_dir / preview_name
        img.convert("RGB").save(preview_path, format="JPEG", quality=82)
        media.preview_file.name = f"media_previews/{preview_name}"
        media.save(update_fields=["preview_file"])
        return f"preview-generated:{media.id}"
    except Exception:
        # fallback for non-image files or missing pillow/ffmpeg
        return f"preview-skipped:{media.id}"
