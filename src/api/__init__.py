from api.auth import auth_router


def router_init(app):
    routers = [auth_router]
    for router in routers:
        app.include_router(router)


__all__ = [router_init]
