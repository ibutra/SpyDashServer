def socketexpose(func):
    """Decorator to expose functions over websocket"""
    func.socketexposed = True
    return func


def updatetask(interval=10):
    def decorator(func):
        func.interval = interval
        func.updater = True
        return func
    return decorator
