#######################
# Agente Basico De IA #
# Agente              #
#######################

# Importacion para el ambiente
from dotenv import load_dotenv

# Importacion para el LLM
from groq import Groq

# Importacion para el manejo de sistema
import os

# Importacion para el uso de formato JSON
import json

# Importacion para el manejo de fechas y zonas horarias
from pathlib import Path

# Importacion para el manejo memoria y herramientas#
from basic_memory import BasicMemory
from intermediate_tools import IntermediateTools



# La configuración local es opcional; en la nube se utilizan Secrets.
load_dotenv(Path(__file__).with_name(".env"))
MEMORY_MAX_MESSAGES = 10
MAX_TOOL_ROUNDS = 8


def get_client(api_key=None):
    """Crea el cliente al utilizarlo, sin exigir una clave al importar el módulo."""
    key = (api_key or os.environ.get("GROQ_API_KEY", "")).strip()
    if not key or key == "coloca_aqui_tu_api_key":
        raise ValueError("Configura GROQ_API_KEY en Secrets o en tu archivo .env local.")
    return Groq(api_key=key, timeout=60.0, max_retries=1)


SYSTEM_PROMPT = f"""
Eres un asistente económico que habla en español y responde de manera breve, clara y sencilla.

Herramientas:
- consultar_tipo_cambio_api consulta el tipo de cambio actual de una moneda respecto al quetzal de Guatemala.
- Para consultar el tipo de cambio, el código de la moneda es obligatorio, por ejemplo USD.
- consultar_inflacion_pais consulta en el Banco Mundial la inflación de un país en un año determinado.
- consultar_pib_per_capita consulta en el Banco Mundial el PIB total y la población de un país, y calcula su PIB per cápita.
- Para consultar_pib_per_capita, el año es opcional. Si el usuario indica un año, debes enviarlo a la herramienta. Si no indica un año, utiliza el último disponible.
- Al responder sobre el PIB per cápita, indica el PIB total, la población, el año, el PIB per cápita y la fuente.
- consultar_crecimiento_economico consulta en el Banco Mundial el crecimiento real del PIB de un país en un año determinado.
- consultar_deuda_publica consulta en el Fondo Monetario Internacional la deuda bruta del gobierno general como porcentaje del PIB de un país en un año determinado.
- Si no existen datos de deuda para el año solicitado, debes informarlo claramente y no inventar valores.
- Al responder sobre deuda pública, indica el país, el año, el porcentaje del PIB y la fuente.
- consultar_desempleo_pais consulta en el Banco Mundial la tasa de desempleo de un país en un año determinado.
- Al responder sobre desempleo, indica el país, el año, el porcentaje de la población activa y la fuente.
- consultar_indicadores_periodo consulta el PIB total, la población, el PIB per cápita, la inflación, el crecimiento económico, la deuda pública y el desempleo de un país durante un rango de años.

Instrucciones:
- Cuando el usuario solicite un indicador específico, utiliza la herramienta correspondiente y explica brevemente el resultado.
- Puedes utilizar formato Markdown únicamente cuando sea necesario presentar tablas.
- Cuando el usuario solicite una tabla, comparación o información de varios años, utiliza consultar_indicadores_periodo en lugar de llamar individualmente a cada herramienta.
- Presenta los resultados en una tabla Markdown con una fila por año.
- Incluye siempre la columna Año y muestra únicamente los indicadores solicitados por el usuario.
- Si el usuario solicita todos los indicadores, utiliza las columnas: Año, PIB total, Población, PIB per cápita, Inflación, Crecimiento, Deuda pública y Desempleo.
- Si el usuario solicita indicadores específicos, no agregues columnas que no haya solicitado.- Presenta el PIB total en miles de millones de USD y la población en millones de habitantes.
- Presenta el PIB per cápita en USD y los demás indicadores en porcentajes.
- Si un valor no está disponible, escribe N/D y no inventes información.
- Debajo de la tabla menciona solamente las fuentes correspondientes a los indicadores mostrados. El PIB, la población, la inflación, el crecimiento y el desempleo provienen del Banco Mundial; la deuda pública proviene del Fondo Monetario Internacional.
- No presentes una serie de datos en un solo párrafo.
- Después de la tabla, agrega una interpretación breve de las tendencias más importantes.espués de la tabla, agrega una interpretación breve de los resultados.
- No repitas información innecesariamente.
- No inventes datos, monedas, unidades, años ni fuentes.
- Presenta los resultados en texto simple para que se vean correctamente en la terminal.
- Nunca describas el PIB per cápita como ingreso per cápita o ingreso promedio. Debes llamarlo PIB per cápita o producción económica por habitante.- Basa tus interpretaciones únicamente en los resultados obtenidos mediante las herramientas.
- Evita conclusiones exageradas o afirmaciones que no puedan justificarse con los indicadores.
- Cuando el usuario solicite una gráfica de uno o varios indicadores históricos, utiliza consultar_indicadores_periodo.
- Cuando se solicite una gráfica, genera primero una tabla Markdown con la columna Año y únicamente los indicadores solicitados.
- No incluyas datos adicionales que el usuario no haya solicitado en la gráfica.
- La interfaz utilizará la tabla Markdown para construir automáticamente la gráfica.
- Para gráficas históricas no incluyas el tipo de cambio, porque esta herramienta solamente consulta el valor actual.


Análisis general:
- Cuando el usuario solicite un análisis general, utiliza todas las herramientas económicas disponibles.
- Utiliza el mismo año para la inflación, el PIB per cápita, el crecimiento económico, la deuda pública y el desempleo.
- Si el usuario no indica un año, utiliza 2023 como año de comparación.
- Para el tipo de cambio utiliza USD automáticamente, sin solicitar la moneda.
- Aclara que el tipo de cambio corresponde a la fecha actual y no necesariamente al año de los demás indicadores.
- Primero presenta por separado los resultados de cada indicador y su fuente.
- Después de presentar todos los indicadores, agrega siempre un párrafo titulado "Resumen breve:".
- En el resumen breve, interpreta conjuntamente el crecimiento económico, la inflación, la deuda pública, el desempleo, el PIB per cápita y el tipo de cambio.
- No te limites a repetir los valores; explica de manera sencilla qué muestran en conjunto sobre la economía del país.
- El resumen breve debe contener entre tres y cinco oraciones.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_tipo_cambio_api",
            "description": (
                "Llama a esta funcion para consultar el tipo de cambio de una moneda "
                "respecto al quetzal de Guatemala. "
                "Se debe enviar como argumento el codigo de la moneda que se desea consultar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "moneda": {
                        "type": "string",
                        "description": "Codigo de la moneda que se desea consultar, por ejemplo USD"
                    }
                },
                "required": ["moneda"]
            }
        }
    },

    #consultar_inflacion_pais
    {
        "type": "function",
        "function": {
            "name": "consultar_inflacion_pais",
            "description": (
                "Consulta en el Banco Mundial la tasa de inflacion "
                "de un pais durante un año determinado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o codigo del pais, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },
                    "anio": {
                        "type": "integer",
                        "description": (
                            "Año que se desea consultar, por ejemplo 2024."
                        )
                    }
                },
                "required": ["pais", "anio"]
            }
        }
    },

    #consultar_pib_per_capita
    {
        "type": "function",
        "function": {
            "name": "consultar_pib_per_capita",
            "description": (
                "Consulta en el Banco Mundial el PIB total y la "
                "poblacion de un pais para calcular su PIB per capita."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o codigo del pais, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },

                    "anio": {
                        "type": "integer",
                        "description": (
                            "Año que se desea consultar. Es opcional; "
                            "si no se proporciona, se usa el último "
                            "año disponible."
                        )
                    }                
                },
                "required": ["pais"]
            }
        }
    },

    #consultar_crecimiento_economico
    {
        "type": "function",
        "function": {
            "name": "consultar_crecimiento_economico",
            "description": (
                "Consulta en el Banco Mundial la tasa de crecimiento "
                "real del PIB de un pais en un año determinado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o codigo del pais, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },
                    "anio": {
                        "type": "integer",
                        "description": (
                            "Año que se desea consultar, por ejemplo 2024."
                        )
                    }
                },
                "required": ["pais", "anio"]
            }
        }
    },

    #consultar_deuda_publica
    {
        "type": "function",
        "function": {
            "name": "consultar_deuda_publica",
            "description": (
                "Consulta en el Fondo Monetario Internacional la deuda "
                "bruta del gobierno general como porcentaje del PIB "
                "para un pais y año."
            ),
            
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o codigo del pais, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },
                    "anio": {
                        "type": "integer",
                        "description": "Año que se desea consultar."
                    }
                },
                "required": ["pais", "anio"]
            }
        }
    },

    #consultar_desempleo_pais"
    {
        "type": "function",
        "function": {
            "name": "consultar_desempleo_pais",
            "description": (
                "Consulta en el Banco Mundial la tasa de desempleo "
                "de un pais en un año determinado."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o codigo del pais, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },
                    "anio": {
                        "type": "integer",
                        "description": "Año que se desea consultar."
                    }
                },
                "required": ["pais", "anio"]
            }
        }
    },

        {
        "type": "function",
        "function": {
            "name": "consultar_indicadores_periodo",
            "description": (
                "Consulta varios indicadores económicos de un país "
                "durante un periodo y devuelve una fila por cada año. "
                "Incluye PIB total, población, PIB per cápita, "
                "inflación, crecimiento, deuda pública y desempleo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pais": {
                        "type": "string",
                        "description": (
                            "Nombre o código del país, "
                            "por ejemplo Guatemala o GTM."
                        )
                    },
                    "anio_inicio": {
                        "type": "integer",
                        "description": (
                            "Primer año del periodo que se desea consultar."
                        )
                    },
                    "anio_final": {
                        "type": "integer",
                        "description": (
                            "Último año del periodo que se desea consultar."
                        )
                    }
                },
                "required": [
                    "pais",
                    "anio_inicio",
                    "anio_final"
                ]
            }
        }
    }

]



def process_response(client:Groq, memory_messages: list[dict], user_text:str):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory_messages[-MEMORY_MAX_MESSAGES:])
    messages.append({"role": "user", "content": user_text})
    
    for _ in range(MAX_TOOL_ROUNDS):
        resp = client.chat.completions.create(
            model=os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=messages,
            tools=TOOLS
        )

        msg = resp.choices[0].message
        
        # Si no hay llamados a herramientas, entonces ya regresamos la respuesta
        if not getattr(msg, "tool_calls", None):
            return msg.content or ""
        
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })
        
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")
            
            tools = IntermediateTools()

            if name == "consultar_tipo_cambio_api":
                result = tools.consultar_tipo_cambio_api(
                    moneda=args["moneda"]
                )

            #consultar_inflacion_pais
            elif name == "consultar_inflacion_pais":
                result = tools.consultar_inflacion_pais(
                    pais=args["pais"],
                    anio=args["anio"]
                )

            #consultar_pib_per_capita
            elif name == "consultar_pib_per_capita":
                result = tools.consultar_pib_per_capita(
                    pais=args["pais"],
                    anio=args.get("anio")
                )

            #consultar_crecimiento_economico
            elif name == "consultar_crecimiento_economico":
                result = tools.consultar_crecimiento_economico(
                    pais=args["pais"],
                    anio=args["anio"]
                )

            #consultar_deuda_publica
            elif name == "consultar_deuda_publica":
                result = tools.consultar_deuda_publica(
                    pais=args["pais"],
                    anio=args["anio"]
                )

        
            #consultar_desempleo_pais
            elif name == "consultar_desempleo_pais":
                result = tools.consultar_desempleo_pais(
                    pais=args["pais"],
                    anio=args["anio"]

            #consultar_indicadores_periodo"      
                )
            elif name == "consultar_indicadores_periodo":
                result = tools.consultar_indicadores_periodo(
                    pais=args["pais"],
                    anio_inicio=args["anio_inicio"],
                    anio_final=args["anio_final"]
                )

            else:
                print(f"Se intentó llamar a una herramienta desconocida {name}")
                result = {"error": f"Herramienta desconocida: {name}"}
                
            # Agregar a los mensajes el resultado del llamado de la herramienta
            # Esto lo recibirá el modelo al continuar la iteración
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

    return (
        "La consulta requirió demasiadas llamadas a herramientas. "
        "Intenta con un indicador o un periodo más corto."
    )


if __name__ == "__main__":
    print("Agente Basico De IA")
    client = get_client()
    memory = BasicMemory(max_messages=MEMORY_MAX_MESSAGES)

    while True:

        user_text = input("Tú: ").strip()

        if not user_text:
            continue

        if user_text.lower() in ("exit", "salir"):
            print("Hasta luego!")
            break

        assistant_text = process_response(
            client,
            memory.messages(),
            user_text
        )

        print(f"Agente: {assistant_text}")

        # Actualizar la memoria
        memory.add("user", user_text)
        memory.add("assistant", assistant_text)