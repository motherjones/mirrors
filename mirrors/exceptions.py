class LockEnforcementError(Exception):
    locking_user = None
    lock_expires_at = None

    def __init__(self, *args, **kwargs):
        if 'locking_user' in kwargs:
            self.locking_user = kwargs['locking_user']

        if 'expires_at' in kwargs:
            self.expires_at = kwargs['expires_at']
