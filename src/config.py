class BaseConfig:
    """
    静态配置基本类
    """
    HOST = "127.0.0.1"
    PORT = 8080
    RELOAD = True
    # 路径配置
    LOG_PATH = "../logs"
    DB_PATH = "./resources/data.db"


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
