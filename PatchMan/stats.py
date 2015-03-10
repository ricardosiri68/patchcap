import time
import logging

logger = logging.getLogger(__name__)


class PatchStat(object):

    MAX_FAILURES = 1000
    _found = 0
    _total = 0
    _detected = 0
    _failures = 0

    def __init__(self):
        logger.info("Iniciando aplicacion")
        self.reset()

    def reset(self):
        self._found = 0
        self._total = 0
        self._failures = 0
        self._detected = 0

    def error(self, e):
        self._failures += 1
        logger.error("No se pudo obtener la imagen")
	logger.error(e)
        if self._failures > PatchStat.MAX_FAILURES: 
            logger.fatal("No se pueden obtener imagenes (repetido %s veces)"%(self.MAX_FAILURES))
            return false

    def found(self):
        self._found += 1

    def detected(self):
        self._detected += 1

    def count(self):
        self._total += 1

    def show(self):
        logger.info(
            "Detectadas correctamente %d/%d", self._found, self._detected
        )
        logger.info(
            "Se encontraron %d errores al procesar %d imagenes",
            self._failures,
            self._total
        )
