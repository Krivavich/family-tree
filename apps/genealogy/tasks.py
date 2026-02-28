try:
    from celery import shared_task
except Exception:  # pragma: no cover
    def shared_task(func=None, **kwargs):
        def decorator(f):
            return f

        return decorator(func) if func else decorator


@shared_task
def generate_media_preview(media_asset_id: int) -> str:
    """Stub task: generate preview image/video thumbnail for MediaAsset.

    In next iteration connect ffmpeg/Pillow and save to MediaAsset.preview_file.
    """
    return f"preview-generation-scheduled:{media_asset_id}"
