import os


class BaseConfig:
    """
    静态配置基本类
    根路径：src文件夹
    """
    HOST = "127.0.0.1"
    PORT = 8080
    RELOAD = True
    # 路径配置
    LOG_PATH = "../logs"
    RESOURCE_PATH = "./resources"
    DB_PATH = os.path.join(RESOURCE_PATH, "data.db")


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
