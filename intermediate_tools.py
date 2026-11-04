#######################
# Agente Basico De IA #
# Herramientas        #
#######################

# Importacion para el manejo de sistema
import os
import requests

class IntermediateTools:

    def __init__(self):
        pass

    # Buscar un país dentro de la API del Banco Mundial
    def obtener_codigo_pais_banco_mundial(self, pais: str):
        if not pais:
            return None

        url = (
            "https://api.worldbank.org/v2/country"
            "?format=json&per_page=400"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        datos = response.json()

        if not datos or len(datos) < 2:
            return None

        pais_buscado = pais.strip().casefold()

        for registro in datos[1]:
            opciones = [
                str(registro.get("name", "")).casefold(),
                str(registro.get("id", "")).casefold(),
                str(registro.get("iso2Code", "")).casefold()
            ]

            if pais_buscado in opciones:
                return {
                    "codigo": registro.get("id"),
                    "nombre": registro.get("name")
                }

        return None
    
    # Herramienta para consultar el tipo de cambio
    def consultar_tipo_cambio_api(self, moneda: str):
        print(f"Herramienta consultar_tipo_cambio_api llamada con moneda: {moneda}")

        if not moneda:
            return "Error: Se requiere el código de la moneda para obtener el tipo de cambio."

        # URL del servicio para obtener el tipo de cambio según la moneda:
        url = (
            f"https://open.er-api.com/v6/latest/{moneda.upper()}"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
            return response.json()  # Intentar decodificar la respuesta como JSON
        except Exception as e:
            print(f"Error al obtener_tipo_cambio_api: {moneda}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio para la moneda: {moneda}"

  

    # Consultar la inflación de un país en el Banco Mundial
    def consultar_inflacion_pais(self, pais: str, anio: int):
        print(
            "Herramienta consultar_inflacion_pais llamada con "
            f"pais: {pais}, anio: {anio}"
        )

        try:
            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]
            anio = str(int(anio))

            url = (
                f"https://api.worldbank.org/v2/country/{codigo}"
                "/indicator/FP.CPI.TOTL.ZG"
                f"?date={anio}&format=json"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            datos = response.json()

            if (
                not datos
                or len(datos) < 2
                or not datos[1]
                or datos[1][0].get("value") is None
            ):
                return (
                    f"No hay información de inflación para "
                    f"{nombre} en {anio}."
                )

            inflacion = float(datos[1][0]["value"])

            return {
                "pais": nombre,
                "anio": anio,
                "inflacion_anual": round(inflacion, 2),
                "unidad": "porcentaje",
                "fuente": "Banco Mundial"
            }

        except Exception as e:
            print(f"Error al consultar inflación: {e}")
            return (
                f"ERROR: No se pudo consultar la inflación "
                f"de {pais} en {anio}."
            )


    
    # Consultar y calcular el PIB per capita de un pais
    def consultar_pib_per_capita(self, pais: str, anio=None):
        print(
            "Herramienta consultar_pib_per_capita llamada con "
            f"pais: {pais}"
        )

        try:
            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]

            if anio is not None:
                anio = str(int(anio))
                filtro = f"?date={anio}&format=json"
            else:
                filtro = "?format=json&mrnev=20&per_page=20"

            url_pib = (
                f"https://api.worldbank.org/v2/country/{codigo}"
                "/indicator/NY.GDP.MKTP.CD"
                f"{filtro}"
            )

            url_poblacion = (
                f"https://api.worldbank.org/v2/country/{codigo}"
                "/indicator/SP.POP.TOTL"
                f"{filtro}"
            )

            respuesta_pib = requests.get(url_pib, timeout=30)
            respuesta_poblacion = requests.get(
                url_poblacion,
                timeout=30
            )

            respuesta_pib.raise_for_status()
            respuesta_poblacion.raise_for_status()

            datos_pib = respuesta_pib.json()
            datos_poblacion = respuesta_poblacion.json()

            if (
                len(datos_pib) < 2
                or len(datos_poblacion) < 2
                or not datos_pib[1]
                or not datos_poblacion[1]
            ):
                return (
                    f"No hay información suficiente para calcular "
                    f"el PIB per cápita de {nombre}."
                )

            pib_por_anio = {
                registro["date"]: registro["value"]
                for registro in datos_pib[1]
                if registro.get("value") is not None
            }

            poblacion_por_anio = {
                registro["date"]: registro["value"]
                for registro in datos_poblacion[1]
                if registro.get("value") is not None
            }

            anios_comunes = set(pib_por_anio) & set(
                poblacion_por_anio
            )

            if not anios_comunes:
                return (
                    f"No hay datos de PIB y población de {nombre} "
                    f"correspondientes al mismo año."
                )

            ultimo_anio = max(anios_comunes, key=int)
            pib = float(pib_por_anio[ultimo_anio])
            poblacion = float(poblacion_por_anio[ultimo_anio])
            pib_per_capita = pib / poblacion

            return {
                "pais": nombre,
                "anio": ultimo_anio,
                "pib_total_usd": round(pib, 2),
                "poblacion_total": int(poblacion),
                "pib_per_capita_usd": round(pib_per_capita, 2),
                "fuente": "Banco Mundial"
            }

        except Exception as e:
            print(f"Error al consultar PIB per capita: {e}")
            return (
                f"ERROR: No se pudo consultar el PIB per cápita "
                f"de {pais}."
            )


    # Consultar el crecimiento económico de un país
    def consultar_crecimiento_economico(self, pais: str, anio: int):
        print(
            "Herramienta consultar_crecimiento_economico llamada con "
            f"pais: {pais}, anio: {anio}"
        )

        try:
            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]
            anio = str(int(anio))

            url = (
                f"https://api.worldbank.org/v2/country/{codigo}"
                "/indicator/NY.GDP.MKTP.KD.ZG"
                f"?date={anio}&format=json"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            datos = response.json()

            if (
                not datos
                or len(datos) < 2
                or not datos[1]
                or datos[1][0].get("value") is None
            ):
                return (
                    f"No hay información de crecimiento económico "
                    f"para {nombre} en {anio}."
                )

            crecimiento = float(datos[1][0]["value"])

            return {
                "pais": nombre,
                "anio": anio,
                "crecimiento_real_del_pib": round(crecimiento, 2),
                "unidad": "porcentaje anual",
                "fuente": "Banco Mundial"
            }

        except Exception as e:
            print(f"Error al consultar crecimiento económico: {e}")
            return (
                f"ERROR: No se pudo consultar el crecimiento "
                f"económico de {pais} en {anio}."
            )

    # Consultar la deuda pública como porcentaje del PIB en el FMI
    def consultar_deuda_publica(self, pais: str, anio: int):
        print(
            "Herramienta consultar_deuda_publica llamada con "
            f"pais: {pais}, anio: {anio}"
        )

        try:
            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]
            anio = str(int(anio))

            url = (
                "https://www.imf.org/external/datamapper/api/v1/"
                f"GGXWDG_NGDP/{codigo}?periods={anio}"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            datos = response.json()

            valores = (
                datos.get("values", {})
                .get("GGXWDG_NGDP", {})
                .get(codigo, {})
            )

            deuda = valores.get(anio)

            if deuda is None:
                return (
                    f"El FMI no tiene información de deuda pública "
                    f"para {nombre} en {anio}."
                )

            return {
                "pais": nombre,
                "anio": anio,
                "deuda_publica": round(float(deuda), 2),
                "unidad": "porcentaje del PIB",
                "fuente": "Fondo Monetario Internacional"
            }

        except Exception as e:
            print(f"Error al consultar deuda pública: {e}")
            return (
                f"ERROR: No se pudo consultar la deuda pública "
                f"de {pais} en {anio}."
            )

    # Consultar la tasa de desempleo de un país
    def consultar_desempleo_pais(self, pais: str, anio: int):
        print(
            "Herramienta consultar_desempleo_pais llamada con "
            f"pais: {pais}, anio: {anio}"
        )

        try:
            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]
            anio = str(int(anio))

            url = (
                f"https://api.worldbank.org/v2/country/{codigo}"
                "/indicator/SL.UEM.TOTL.ZS"
                f"?date={anio}&format=json"
            )

            response = requests.get(url, timeout=30)
            response.raise_for_status()
            datos = response.json()

            if (
                not datos
                or len(datos) < 2
                or not datos[1]
                or datos[1][0].get("value") is None
            ):
                return (
                    f"El Banco Mundial no tiene información de "
                    f"desempleo para {nombre} en {anio}."
                )

            desempleo = float(datos[1][0]["value"])

            return {
                "pais": nombre,
                "anio": anio,
                "tasa_de_desempleo": round(desempleo, 2),
                "unidad": (
                    "porcentaje de la población activa"
                ),
                "fuente": "Banco Mundial"
            }

        except Exception as e:
            print(f"Error al consultar desempleo: {e}")
            return (
                f"ERROR: No se pudo consultar el desempleo "
                f"de {pais} en {anio}."
            )
    # Consultar varios indicadores económicos durante un periodo
    def consultar_indicadores_periodo(
        self,
        pais: str,
        anio_inicio: int,
        anio_final: int
    ):
        print(
            "Herramienta consultar_indicadores_periodo llamada con "
            f"pais: {pais}, desde {anio_inicio} hasta {anio_final}"
        )

        try:
            anio_inicio = int(anio_inicio)
            anio_final = int(anio_final)

            if anio_inicio > anio_final:
                return (
                    "Error: El año inicial no puede ser mayor "
                    "que el año final."
                )

            if anio_final - anio_inicio > 30:
                return (
                    "Error: El periodo no puede superar 30 años."
                )

            informacion_pais = (
                self.obtener_codigo_pais_banco_mundial(pais)
            )

            if not informacion_pais:
                return f"Error: No se encontró el país: {pais}."

            codigo = informacion_pais["codigo"]
            nombre = informacion_pais["nombre"]

            # Consultar una serie del Banco Mundial
            def consultar_serie_banco_mundial(indicador):
                url = (
                    f"https://api.worldbank.org/v2/country/{codigo}"
                    f"/indicator/{indicador}"
                    f"?date={anio_inicio}:{anio_final}"
                    "&format=json&per_page=1000"
                )

                response = requests.get(url, timeout=30)
                response.raise_for_status()
                datos = response.json()

                if not datos or len(datos) < 2 or not datos[1]:
                    return {}

                return {
                    registro["date"]: registro["value"]
                    for registro in datos[1]
                    if registro.get("value") is not None
                }

            # Series del Banco Mundial
            pib = consultar_serie_banco_mundial(
                "NY.GDP.MKTP.CD"
            )

            poblacion = consultar_serie_banco_mundial(
                "SP.POP.TOTL"
            )

            inflacion = consultar_serie_banco_mundial(
                "FP.CPI.TOTL.ZG"
            )

            crecimiento = consultar_serie_banco_mundial(
                "NY.GDP.MKTP.KD.ZG"
            )

            desempleo = consultar_serie_banco_mundial(
                "SL.UEM.TOTL.ZS"
            )

            # Serie de deuda pública del FMI
            anios = [
                str(anio)
                for anio in range(anio_inicio, anio_final + 1)
            ]

            periodos = ",".join(anios)

            url_deuda = (
                "https://www.imf.org/external/datamapper/api/v1/"
                f"GGXWDG_NGDP/{codigo}?periods={periodos}"
            )

            response_deuda = requests.get(
                url_deuda,
                timeout=30
            )

            response_deuda.raise_for_status()
            datos_deuda = response_deuda.json()

            deuda = (
                datos_deuda.get("values", {})
                .get("GGXWDG_NGDP", {})
                .get(codigo, {})
            )

            # Construir una fila por cada año
            resultados = []

            for anio in anios:
                valor_pib = pib.get(anio)
                valor_poblacion = poblacion.get(anio)

                if (
                    valor_pib is not None
                    and valor_poblacion not in (None, 0)
                ):
                    pib_per_capita = (
                        float(valor_pib) / float(valor_poblacion)
                    )
                else:
                    pib_per_capita = None

                resultados.append({
                    "anio": anio,
                    "pib_total_usd": (
                        round(float(valor_pib), 2)
                        if valor_pib is not None
                        else None
                    ),
                    "poblacion_total": (
                        int(valor_poblacion)
                        if valor_poblacion is not None
                        else None
                    ),
                    "pib_per_capita_usd": (
                        round(pib_per_capita, 2)
                        if pib_per_capita is not None
                        else None
                    ),
                    "inflacion_porcentaje": (
                        round(float(inflacion[anio]), 2)
                        if anio in inflacion
                        else None
                    ),
                    "crecimiento_pib_porcentaje": (
                        round(float(crecimiento[anio]), 2)
                        if anio in crecimiento
                        else None
                    ),
                    "deuda_publica_porcentaje_pib": (
                        round(float(deuda[anio]), 2)
                        if anio in deuda
                        else None
                    ),
                    "desempleo_porcentaje": (
                        round(float(desempleo[anio]), 2)
                        if anio in desempleo
                        else None
                    )
                })

            return {
                "pais": nombre,
                "anio_inicio": anio_inicio,
                "anio_final": anio_final,
                "resultados": resultados,
                "fuentes": {
                    "Banco Mundial": (
                        "PIB, población, inflación, crecimiento "
                        "y desempleo"
                    ),
                    "Fondo Monetario Internacional": (
                        "deuda pública"
                    )
                }
            }

        except Exception as e:
            print(
                "Error al consultar indicadores del periodo: "
                f"{e}"
            )

            return (
                f"ERROR: No se pudieron consultar los indicadores "
                f"de {pais} entre {anio_inicio} y {anio_final}."
            )