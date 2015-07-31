# coding=utf-8


if __name__ == '__main__':
    pass


def notify_client(url, params):
    import requests

    try:
        req = requests.post(url, params)
        if req.status_code == 200:
            data = req.json()
            if data['code'] == 0:
                return True
    except:
        return False
