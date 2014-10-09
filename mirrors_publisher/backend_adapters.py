from django.conf import settings


class BackendAdapter(object):
    def __init__(self, args, **kwargs):
        pass

    def put(self, dest, file):
        raise NotImplementedError


class MockAdapter(BackendAdapter):
    def put(self, dest, file):
        return True


def get_adapter():
    adapter = settings.BACKEND_ADAPTER

    m = __import__(".".join(adapter.split('.')[:-1]))
    klass = getattr(m, adapter.split('.')[-1])

    return klass(**settings.BACKEND_ADAPTER_ARGS)
