from api.auth import auth_router


def router_init(app):
    routers = [auth_router]
    for router in routers:
        app.include_router(router)
    from util import log
    log.info("🌍 路由初始化完成")


__all__ = [router_init]
