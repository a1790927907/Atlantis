import uuid


def get_uuid() -> str:
    return uuid.uuid4().__str__()
