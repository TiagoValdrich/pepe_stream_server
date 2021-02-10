from aiohttp.web import middleware, Request, Response, HTTPForbidden
from os import environ


@middleware
async def authentication(request: Request, handler):
    if "Authorization" in request.headers:
        token_params = request.headers["Authorization"].split(" ")

        if token_params[0] == "Bearer" and token_params[-1] == environ.get(
            "AUTHENTICATION_TOKEN", "default_authentication_token"
        ):
            resp: Response = await handler(request)
            return resp

    raise HTTPForbidden(text="Invalid authentication token!")