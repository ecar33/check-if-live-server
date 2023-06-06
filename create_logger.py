import logging

def create():
    # Create a logger
    logger = logging.getLogger('my_logger')

    # Set the level of this logger to DEBUG. This means it will handle messages of severity DEBUG and above.
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler('logfile')

    # Set the level of the file handler to DEBUG. This means it will handle messages of severity DEBUG and above.
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to the file handler
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger