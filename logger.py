import logging
#generic logging code
def make_logger(logger_name,log_file_name):
    logging_format = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(level = logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging_format)
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(level = logging.DEBUG)
    file_handler.setFormatter(logging_format)
    logger.addHandler(file_handler)
    return logger