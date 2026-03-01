from django.core.exceptions import ValidationError

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def validate_media_upload(file_obj) -> None:
    size = getattr(file_obj, "size", 0)
    if size and size > MAX_UPLOAD_BYTES:
        raise ValidationError("Файл слишком большой. Максимум 20MB.")

    try:
        pos = file_obj.tell()
    except Exception:
        pos = None

    chunk = file_obj.read(8192)
    if EICAR_SIGNATURE in chunk:
        raise ValidationError("Файл отклонён антивирусной проверкой.")

    if pos is not None:
        file_obj.seek(pos)
