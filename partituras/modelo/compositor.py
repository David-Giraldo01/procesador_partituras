from abc import ABC, abstractmethod

from partituras.modelo.errores import (ContieneNumero, ContieneCaracterInvalido, SinNotas, EspacioMultiple, EspacioBordes,)


class ReglaTransformacion(ABC):
    def __init__(self, token: int):
        self.token = token

    @abstractmethod
    def transformar(self, partitura: str) -> str:
        pass

    @abstractmethod
    def revertir(self, partitura: str) -> str:
        pass

    @abstractmethod
    def partitura_valida(self, partitura: str) -> bool:
        pass

    def encontrar_numeros_partitura(self, partitura: str) -> list:
        return [(i, c) for i, c in enumerate(partitura) if c.isdigit()]

    def encontrar_caracteres_invalidos(self, partitura: str) -> list:
        return [(i, c) for i, c in enumerate(partitura) if not c.isascii()]

class ReglaTransposicion(ReglaTransformacion):
    NOTAS = ["do", "re", "mi", "fa", "sol", "la", "si"]

    def partitura_valida(self, partitura: str) -> bool:
        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)
        if numeros:
            mensaje = ", ".join(
                [f"posición {i}: '{c}'" for i, c in numeros])
            errores.append(ContieneNumero(f"La partitura contiene números -> {mensaje}"))

        invalidos_ascii = self.encontrar_caracteres_invalidos(partitura)
        if invalidos_ascii:
            mensaje = ", ".join([f"posición {i}: '{c}'" for i, c in invalidos_ascii])
            errores.append(ContieneCaracterInvalido(f"Caracteres no ASCII encontrados -> {mensaje}"))

        partitura = partitura.lower()
        tokens = partitura.split()

        permitidos = self.NOTAS + ["|", "-"]

        invalidos = [
            token
            for token in tokens
            if token not in permitidos]

        if invalidos: errores.append(
                ContieneCaracterInvalido(f"Tokens inválidos encontrados -> {', '.join(invalidos)}"))

        notas_encontradas = [
            token
            for token in tokens
            if token in self.NOTAS]

        if not notas_encontradas:
            errores.append(
                SinNotas("La partitura no contiene notas válidas")
            )

        if errores:
            raise ExceptionGroup(
                "Errores de validación",
                errores
            )

        return True

    def transformar(self, partitura: str) -> str:
        self.partitura_valida(partitura)

        partitura = partitura.lower()
        tokens = partitura.split()

        resultado = [
            self._mover_nota(token, self.token)
            if token in self.NOTAS
            else token
            for token in tokens]

        return " ".join(resultado)

    def revertir(self, partitura: str) -> str:
        self.partitura_valida(partitura)

        partitura = partitura.lower()
        tokens = partitura.split()

        resultado = [self._mover_nota(token, -self.token)
            if token in self.NOTAS
            else token
            for token in tokens]

        return " ".join(resultado)

    def _mover_nota(self, nota: str, pasos: int) -> str:
        indice = self.NOTAS.index(nota)
        nuevo_indice = (indice + pasos) % len(self.NOTAS)
        return self.NOTAS[nuevo_indice]


class ReglaFrecuencia(ReglaTransformacion):
    FRECUENCIAS = {
        "do": 261,
        "re": 293,
        "mi": 329,
        "fa": 349,
        "sol": 392,
        "la": 440,
        "si": 493,
    }

    def partitura_valida(self, partitura: str) -> bool:
        errores = []

        numeros = self.encontrar_numeros_partitura(partitura)
        if numeros:
            mensaje = ", ".join([f"posición {i}: '{c}'" for i, c in numeros])
            errores.append(
                ContieneNumero(f"La partitura contiene números -> {mensaje}"))

        invalidos_ascii = self.encontrar_caracteres_invalidos(partitura)
        if invalidos_ascii:
            mensaje = ", ".join([f"posición {i}: '{c}'" for i, c in invalidos_ascii])
            errores.append(
                ContieneCaracterInvalido(f"Caracteres no ASCII encontrados -> {mensaje}"))
        if partitura != partitura.strip():
            errores.append(EspacioBordes("La partitura contiene espacios al inicio o final"))

        if "  " in partitura:
            errores.append(EspacioMultiple("La partitura contiene espacios múltiples"))

        partitura = partitura.lower()

        if "|" in partitura or "-" in partitura:
            errores.append(ContieneCaracterInvalido("No se permiten separadores ni silencios"))

        tokens = partitura.split()

        invalidos = [
            token
            for token in tokens
            if token not in self.FRECUENCIAS]

        if invalidos:
           errores.append(ContieneCaracterInvalido(f"Notas inválidas -> {', '.join(invalidos)}"))

        if errores:
         raise ExceptionGroup("Errores de validación", errores)

        return True

    def transformar(self, partitura: str) -> str:
        self.partitura_valida(partitura)

        partitura = partitura.lower()

        return " ".join([
            str(self.FRECUENCIAS[nota] * self.token)
            for nota in partitura.split()
        ])

    def revertir(self, partitura: str) -> str:
        valores = partitura.split()

        frecuencias_reales = [
            int(int(valor) / self.token)
            for valor in valores
        ]

        resultado = [
            self._buscar_nota(freq)
            for freq in frecuencias_reales
        ]

        return " ".join(resultado)

    def _buscar_nota(self, frecuencia: int) -> str:
        for nota, freq in self.FRECUENCIAS.items():
            if freq == frecuencia:
                return nota

        raise ValueError(
            f"No existe una nota para la frecuencia {frecuencia}"
        )


