from logging import Logger
from logging import getLogger, INFO, Formatter, DEBUG
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime


class SingletonLogger:
    def __init__(self, name: str = "logger", level: int = INFO, debug: bool = True) -> None:
        """Use for logging in every file.

        Args:
            name (str, optional): Name of the logger. Defaults to "logger".
            level (int, optional): Level of the default log. Defaults to INFO.
            debug (bool, optional): Activates or deactivates debug log file. Defaults to True.
        """
        
        self.name = name
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        self.debug = debug
        self.level = level

    
    def get_logger(self) -> Logger:
        """Use to get logger instance.

        Returns:
            Logger: Logger
        """
        if not self.logger.handlers:
            
            log_folder = Path(__file__).resolve().parent / "Logs"
            
            if not log_folder.exists():
                log_folder.mkdir(parents=True, exist_ok=True)
            
            formatter = Formatter("%(levelname)s : %(asctime)s : %(message)s", datefmt="%y/%m/%d %H:%M:%S")
            
            log_path = log_folder / f"{self.name}_{datetime.now().strftime('%Y-%m-%d')}.log"
            
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
                debug_log_path = log_folder / f"{self.name}_{datetime.now().strftime('%Y-%m-%d')}_debug.log"
                
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