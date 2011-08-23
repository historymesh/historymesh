import traceback

class ExceptionConsoleMiddleware(object):

    def process_exception(self, request, exception):
        traceback.print_exc()
