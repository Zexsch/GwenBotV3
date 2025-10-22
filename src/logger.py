from logging import Logger
from logging import getLogger, INFO, Formatter, DEBUG
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Type, TypeVar
from datetime import datetime


T = TypeVar('T', bound='SingletonLogger')


class SingletonLogger:
    """Use for logging in every file. Singleton type.
    """
    def __new__(cls: Type[T], *args, **kwargs) -> T:
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonLogger, cls).__new__(cls)
        return cls.instance
    
    def __init__(self, name: str = "logger", level: int = INFO, debug: bool = True) -> None:
        """Use for logging in every file. Singleton type.

        Args:
            name (str, optional): Name of the logger. Defaults to "logger".
            level (int, optional): Level of the default log. Defaults to INFO.
            debug (bool, optional): Activates or deactivates debug log file. Defaults to True.
        """
        if hasattr(self, '_initialised') and self._initialised: # pylint: disable=access-member-before-definition
            return
        
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        self.debug = debug
        self.level = level
        
        self._initialised = True

    
    def get_logger(self) -> Logger:
        """Use to get logger instance.

        Returns:
            Logger: Logger
        """
        
        if not self.logger.handlers:
            
            formatter = Formatter("%(levelname)s : %(asctime)s : %(message)s", datefmt="%y/%m/%d %H:%M:%S")
            
            log_path = Path(__file__).resolve() / "Logs" / f"log_{datetime.now().strftime('%Y-%m-%d')}.log"
            
            file_handler = TimedRotatingFileHandler(
                filename=log_path,
                when='D',
                interval=1,
                backupCount=180,
                encoding='utf-8'
            )
            
            file_handler.setFormatter(formatter)
            file_handler.setLevel(self.level)
            self.logger.addHandler(file_handler)
            
            if self.debug:
                debug_log_path = Path(__file__).resolve() / "Logs" / f"log_{datetime.now().strftime('%Y-%m-%d')}_debug.log"
                
                debug_file_handler = TimedRotatingFileHandler(
                    filename=debug_log_path,
                    when='D',
                    interval=1,
                    backupCount=180,
                    encoding='utf-8'
                )
                
                debug_file_handler.setFormatter(formatter)
                debug_file_handler.setLevel(DEBUG)
                self.logger.addHandler(debug_file_handler)
            
            
        return self.logger    