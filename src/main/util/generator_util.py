from uuid import uuid4


def get_uuid() -> str:
    return uuid4().__str__()


if __name__ == '__main__':
    print(get_uuid())
