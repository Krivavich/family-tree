def send_2fa_code(device_kind: str, target: str, code: str) -> None:
    """Integration hook for email/SMS provider.

    In production, replace with actual email/SMS gateway call and observability.
    """
    # no-op stub for now; intentionally does not log raw code
    _ = (device_kind, target, code)
