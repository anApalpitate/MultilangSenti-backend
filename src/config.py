class BaseConfig:
    """
    静态配置基本类
    """
    HOST = "localhost"
    PORT = 8080
    RELOAD = True


class DevConfig(BaseConfig):
    """
    开发环境配置类
    """
    DEBUG = True
    CLEAN_LOG = True


config_map = {
    "base": BaseConfig,
    "dev": DevConfig,
}


def get_config(env: str = "dev"):
    return config_map.get(env, DevConfig)
