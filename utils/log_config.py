import logging
import os

def init_log() -> logging.Logger:
    """初始化日志系统：返回日志器实例，供其他模块调用"""
    logger = logging.getLogger("mall_system")#给日志器起的名字
    logger.setLevel(logging.INFO)  #仅记录INFO及以上级别日志

    # 存疑：移除重复Handler（避免多次初始化导致日志重复），比如多次调用init_log()时，会添加多个处理器，导致一条日志打印多次
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 创建FileHandler（指定UTF-8编码，解决乱码问题）
    # mode="a"：追加模式（新日志加在文件末尾，不覆盖旧日志）
    log_file = "mall_system.log"
    file_handler = logging.FileHandler(
        log_file, mode="a", encoding="utf-8"
    )

    # 定义日志格式：时间-操作人-操作类型-响应时间-结果
    log_format = logging.Formatter(
        "%(asctime)s - %(user)s - %(operation)s - %(response_time)s - %(result)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    #在其他地方需要记录日志时，只需导入这个logger，然后调用logger.info()记录日志
    file_handler.setFormatter(log_format)

    # 添加Handler到日志器
    logger.addHandler(file_handler)
    return logger

# 全局日志器实例（其他模块导入此实例即可使用）
logger = init_log()