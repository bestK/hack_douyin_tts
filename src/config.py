import logging
import os


def bind_env_variables(cls):
    for attr_name in dir(cls):
        attr_value = getattr(cls, attr_name)
        if isinstance(attr_value, str) and attr_value.startswith("$"):
            env_var_name = attr_value[1:]
            setattr(cls, attr_name, os.getenv(env_var_name))
    return cls


@bind_env_variables
class TTS_CONFIG:
    api_url: str = "$API_URL"
    api_req_key: str = "$API_REQ_KEY"
    api_res_key: str = "$API_RES_KEY"
    api_params: str = "$API_PARAMS"
    api_sec: str = "$API_SEC"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_level = record.levelname
        log_color = LOG_LEVEL_COLORS.get(log_level, "")
        record.log_color = log_color
        return super().format(record)


# 创建自定义的ColoredFormatter实例
formatter = ColoredFormatter(
    fmt="%(log_color)s%(levelname)s\033[0m  - %(asctime)s - %(name)s - %(lineno)s - %(message)s"
)

# 创建自定义的StreamHandler，并将ColoredFormatter配置为其格式化器
handler = logging.StreamHandler()
handler.setFormatter(formatter)


def get_logger():
    logging.basicConfig(
        format="%(log_color)s%(levelname)s\033[0m  - %(asctime)s - %(name)s - %(lineno)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(__name__)

    logger.addHandler(handler)
    if "DEBUG" in os.environ:
        logger.setLevel(logging.DEBUG)
    return logger


# 设置日志级别颜色的映射关系
LOG_LEVEL_COLORS = {
    "DEBUG": "\033[1;32m",  # 绿色
    "INFO": "\033[1;34m",  # 蓝色
    "WARNING": "\033[1;33m",  # 黄色
    "ERROR": "\033[1;31m",  # 红色
    "CRITICAL": "\033[1;41m",  # 红底白字，表示严重错误
}
