import logging
import json

from logging.handlers import RotatingFileHandler       # rotacao por tamanho
from logging.handlers import TimedRotatingFileHandler  # rotacao por dia

from pathlib import Path

# Configuração básica do logger
logging.basicConfig(
    level=logging.DEBUG,  # Nível mínimo de log
    format="%(asctime)s [%(levelname)s] (%(name)s): %(message)s",
    handlers=[
        logging.StreamHandler(),          # Saída no console
        #logging.FileHandler(log_file)     # Saída em arquivo
    ]
)

# Objeto pre-configurado para ser acessado por outros modulos
logger = logging.getLogger(None)

# Define o arquivo de saída
def set_file(filename: str):
    logger.debug(f"set_file(): ${filename}")

    if filename:
        # Formatter para arquivo (JSON estruturado)
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    "time": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                return json.dumps(log_record)

        # Handler para arquivo com rotação por tamanho
        file_handler = RotatingFileHandler(filename, maxBytes=1024*1024, backupCount=7, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())

        # Handler para arquivo com rotação diária
        #file_handler2 = TimedRotatingFileHandler(filename, when="midnight", interval=1, backupCount=7, encoding="utf-8")
        #file_handler.setFormatter(JsonFormatter())

        # Adiciona na configuração do logger
        logger.addHandler(file_handler)


if __name__ == '__main__':
    logger.warning("Log executado a partir do próprio modulo")

    # Exemplo: Definindo arquivo de saida na pasta do arquivo atual
    _base_dir = Path(__file__).parent
    _module_name = Path(__file__).stem
    _log_file = _base_dir / f"{_module_name}.log"
    set_file(_log_file)

    # Exemplo Registrando mensagens no log para este módulo
    new_logger = logging.getLogger(Path(__file__).stem)
    new_logger.info("Novo modulo para registrar nas mensagens")



