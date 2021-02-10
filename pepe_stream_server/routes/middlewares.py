from aiohttp.web import middleware, Request, Response, HTTPForbidden
from os import environ


@middleware
async def authentication(request: Request, handler):
    if request.path and request.path[0] == "/":
        base_path = request.path[1:].split("/")[0]

        if not base_path or base_path in ["live", "offer"]:
            return await handler(request)

    if "Authorization" in request.headers:
        token_params = request.headers["Authorization"].split(" ")

        if token_params[0] == "Bearer" and token_params[-1] == environ.get(
            "AUTHENTICATION_TOKEN", "default_authentication_token"
        ):
            return await handler(request)

    raise HTTPForbidden(text="Invalid authentication token!")