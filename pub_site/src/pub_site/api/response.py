from flask import jsonify


# json api specification

def success(_data=None, _merge=None, **kwargs):
    data = _data
    if kwargs:
        data = kwargs

    res = {'ret': True, 'data': data}
    if _merge:
        res.update(_merge)
    return jsonify(res)


def failed(msg, _data=None, _merge=None, **kwargs):
    data = _data
    if kwargs:
        data = kwargs

    res = {'ret': False, 'fail': 'fail', 'msg': msg, 'data': data}
    if _merge:
        res.update(_merge)
    return jsonify(res)


def error(msg, _data=None, _merge=None, **kwargs):
    data = _data
    if kwargs:
        data = kwargs

    res = {'ret': False, 'fail': 'error', 'msg': msg, 'data': data}
    if _merge:
        res.update(_merge)
    return jsonify(res)


def form_is_invalid(errors):
    if '__all__' in errors:
        msg = errors['__all__'][0]
    else:
        msg = errors.values()[0][0]
    return failed(msg, **errors)
