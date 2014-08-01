from django.http import JsonResponse

from mirrors.views import LockEnforcementError


class MirrorsLockEnforcementMiddleware(object):
    def process_exception(self, request, exception):
        if isinstance(exception, LockEnforcementError):
            return JsonResponse({'message': 'This component is locked'},
                                status=403)
