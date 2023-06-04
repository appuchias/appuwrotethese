from django.contrib import messages
from django.utils.translation import gettext_lazy as _

MESSAGES = [
    # {"type": "info", "text": _("The web is under development. It HAS bugs"), "path": ""},
    {
        "type": "warning",
        "text": _("Province searching might be broken") + ".",
        "path": "gas",
    },
]


class PermanentMessagesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.levels = {
            "debug": messages.DEBUG,
            "info": messages.INFO,
            "success": messages.SUCCESS,
            "warning": messages.WARNING,
            "error": messages.ERROR,
        }

    def __call__(self, request):
        # Here code before view
        if len(messages.get_messages(request)) < len(MESSAGES) and request.path != "/":
            for message in MESSAGES:
                if message.get("path", "") in request.path:
                    messages.add_message(
                        request, self.levels[message["type"]], message["text"]
                    )

        response = self.get_response(request)
        # Here code after view

        return response
