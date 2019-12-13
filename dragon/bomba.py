import json

from .grupo import Grupo


class Bomba(Grupo):

    def __init__(self, idGrupo=0, idSubsistema=0, nombre='', descripcion='', foto='', presion='0', flujo='0', voltaje1='0', voltaje2='0',
                 voltaje3='0', corriente1='0', corriente2='0', corriente3='0', fase1=0,
                 fase2=0, fase3=0, estado=0, modoOperacion=0, idDispositivo='', conectado=-1, coordinador=''):
        super().__init__(idGrupo, idSubsistema, nombre, descripcion, foto)
        self._presion = float(presion)
        self._flujo = float(flujo)
        self._voltaje1 = voltaje1
        self._voltaje2 = voltaje2
        self._voltaje3 = voltaje3
        self._corriente1 = corriente1
        self._corriente2 = corriente2
        self._corriente3 = corriente3
        self._fase1 = fase1
        self._fase2 = fase2
        self._fase3 = fase3
        self._estado = estado
        self._modoOperacion = modoOperacion
        self._idDispositivo = idDispositivo
        self._conectado = conectado
        self._coordinador = coordinador
        self.coordinador = None

    def set(self, registro):
        super().set(registro)
        self._presion = float(registro['presion'])
        self._flujo = float(registro['flujo'])
        self._voltaje1 = registro['voltaje1']
        self._voltaje2 = registro['voltaje2']
        self._voltaje3 = registro['voltaje3']
        self._corriente1 = registro['corriente1']
        self._corriente2 = registro['corriente2']
        self._corriente3 = registro['corriente3']
        self._fase1 = int(registro['fase1'])
        self._fase2 = int(registro['fase2'])
        self._fase3 = int(registro['fase3'])
        self._estado = int(registro['estado'])
        self._modoOperacion = int(registro['modoOperacion'])
        self._idDispositivo = str(registro['idDispositivo'])
        self._conectado = int(registro['conectado'])
        self._coordinador = int(registro['coordinador'])

    def setCoordinador(self, coordinador):
        self.coordinador = coordinador

    @property
    def getPresion(self):
        return "%0.2f" % self._presion

    @property
    def getFlujo(self):
        return "%0.2f" % self._flujo

    @property
    def getVoltaje1(self):
        return self._voltaje1

    @property
    def getVoltaje2(self):
        return self._voltaje2

    @property
    def getVoltaje3(self):
        return self._voltaje3

    @property
    def getCorriente1(self):
        return self._corriente1

    @property
    def getCorriente2(self):
        return self._corriente2

    @property
    def getCorriente3(self):
        return self._corriente3

    @property
    def getFase1(self):
        return self._fase1

    @property
    def getFase2(self):
        return self._fase2

    @property
    def getFase3(self):
        return self._fase3

    @property
    def getEstado(self):
        return self._estado

    @property
    def getModoOperacion(self):
        return self._modoOperacion

    @property
    def getIdDispositivo(self):
        return self._idDispositivo

    @property
    def getConectado(self):
        return self._conectado

    @property
    def getIdCoordinador(self):
        return self._coordinador

    @property
    def getCoordinador(self):
        return self.coordinador

    def json(self):
        data = super().jsonData()
        data.voltaje1 = self._voltaje1
        data.voltaje2 = self._voltaje2
        data.voltaje3 = self._voltaje3
        data.corriente1 = self._corriente1
        data.corriente2 = self._corriente2
        data.corriente3 = self._corriente3
        data.fase1 = self._fase1
        data.fase2 = self._fase2
        data.fase3 = self._fase3
        data.estado = self._estado
        data.modoOperacion = self._modoOperacion
        data.idDispositivo = self._idDispositivo
        data.conectado = self._conectado
        data.coordinador = self._coordinador
        return json.loads(data.dumps())

    def __eq__(self, other):
        if not isinstance(other, Bomba):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self._presion == other._presion and self._flujo == other._flujo and self._voltaje1 == other._voltaje1 and self._voltaje2 == other._voltaje2 and self._voltaje3 == other._voltaje3 and self._corriente1 == other._corriente1 and self._corriente2 == other._corriente2 and self._corriente3 == other._corriente3 and self._fase1 == other._fase1 and self._fase2 == other._fase2 and self._fase3 == other._fase3 and self._estado == other._estado and self._modoOperacion == other._modoOperacion and self._idDispositivo and self._conectado == other._conectado
