import base64


def encode_uuid(value):
    return base64.b64encode(value)


def decode_uuid(uuid):
    return base64.b64decode(uuid)
