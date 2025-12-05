import logging
import sys
import structlog
from app.core.config import settings


def setup_logging():
    """
    Configure structlog and standard logging to work together.
    Outputs traditional log format in development and JSON logs in production.
    """

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    is_production = settings.ENV.lower() == "production"

    # 1. Configure Structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_production:
        processors.extend(
            [
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.dict_tracebacks,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ]
        )
    else:
        # In Dev, just wrap it so it can be passed to standard logger
        processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 2. Configure Standard Library Logging
    handler = logging.StreamHandler(sys.stdout)

    if is_production:
        # Production: Use JSON Renderer via ProcessorFormatter
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processors=[structlog.processors.JSONRenderer()],
            )
        )
    else:

        class ColoredStructlogFormatter(logging.Formatter):
            # ANSI color codes
            COLORS = {
                "DEBUG": "\033[36m",  # Cyan
                "INFO": "\033[32m",  # Green
                "WARNING": "\033[33m",  # Yellow
                "ERROR": "\033[31m",  # Red
                "CRITICAL": "\033[41m",  # Red background
            }
            RESET = "\033[0m"
            GREY = "\033[90m"

            def format(self, record):
                # Unpack structlog dict if present
                message_str = record.msg
                if isinstance(record.msg, dict):
                    event_dict = record.msg
                    message_str = event_dict.get("event", "")
                    extra = {k: v for k, v in event_dict.items() if k not in ["event"]}
                    if extra:
                        message_str = f"{message_str} {self.GREY}{extra}{self.RESET}"
                elif record.args:
                    # Handle Uvicorn access logs with positional args
                    try:
                        message_str = record.msg % record.args
                    except Exception:
                        message_str = f"{record.msg} {record.args}"

                # Colorize Levels & Logger Name
                color = self.COLORS.get(record.levelname, self.RESET)
                levelname_colored = f"{color}{record.levelname:<8}{self.RESET}"
                name_colored = f"{self.GREY}{record.name}{self.RESET}"

                # Format Timestamp
                asctime = self.formatTime(record, self.datefmt)

                # Final Layout: Time | Level | Logger | Message
                return f"{self.GREY}{asctime}{self.RESET} | {levelname_colored} | {name_colored} | {message_str}"

        handler.setFormatter(ColoredStructlogFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    # 3. Hijack Uvicorn Loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logger = logging.getLogger(logger_name)
        logger.handlers = [handler]
        logger.propagate = False
        logger.setLevel(log_level)

    # 4. Reduce noise
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("llama_index_instrumentation.dispatcher").setLevel(
        logging.WARNING
    )


logger = structlog.get_logger()
