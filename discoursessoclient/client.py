import base64
import hashlib
import hmac
import secrets
import urllib.parse

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings


class DiscourseSsoClientMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.path == '/sso/init':
            return self.sso_init(request)
        elif request.path == '/sso/login':
            return self.sso_login(request)
        else:
            return self.get_response(request)

    def sso_init(self, request):
        nonce = request.session['sso_nonce'] = secrets.token_hex(16)
        return_url = settings.SSO_CLIENT_BASE_URL
        payload = f'nonce={nonce}&return_sso_url={return_url}/login'
        payload = base64.b64encode(bytes(payload, encoding='utf-8'))
        signature = self.sign_payload(str(payload))
        payload = urllib.parse.quote_plus(str(payload))
        to_url = f'{settings.SSO_PROVIDER_URL}?sso={payload}&sig={signature}'
        return HttpResponseRedirect(to_url)

    # Generates signature for utf-8 string payload.
    def sign_payload(self, payload):
        return hmac.new(bytes(settings.SSO_SECRET, encoding='utf-8'),
                        bytes(payload, encoding='utf-8'),
                        digestmod=hashlib.sha256).hexdigest()
