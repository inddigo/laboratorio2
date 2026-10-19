# Laboratorio 2 — Web Scraping, procesamiento y buscador TF-IDF

**Asignatura:** Ingeniería Web Avanzada (OII436-1)  
**Integrantes:** Fernando Figueroa, German Oses, Joshua Villavicencio  
**Repositorio:** https://github.com/inddigo/laboratorio2  
**Fuente de datos:** https://books.toscrape.com/ (solo la primera página, sin paginación).

## 1. Descripción del proyecto

Este laboratorio implementa un proceso de extracción, limpieza y recuperación de información de un catálogo de libros. Primero se obtienen los registros mediante Web Scraping con `requests` y `BeautifulSoup`; luego se procesan con `pandas` y se guardan en `libros.csv`. Finalmente, un buscador utiliza TF-IDF y similitud del coseno para ordenar títulos según su relevancia para una consulta.

## 2. Archivos del repositorio

```text
laboratorio2/
├── scraper.py          # Extracción de libros desde la primera página
├── procesamiento.py    # Limpieza, indicadores y exportación a CSV
├── buscador.py         # Búsqueda de títulos mediante TF-IDF
├── libros.csv          # Datos extraídos y procesados
├── requirements.txt    # Dependencias de Python
├── README.md           # Instrucciones y evidencias
└── .gitignore          # Exclusión de .venv y archivos temporales
```

El entorno virtual `.venv/` **no se incluye** en el repositorio.

## 3. Preparación y entorno virtual

Se necesita Python, Git y acceso a Internet para ejecutar el scraping. Abrir una terminal y clonar el repositorio:

```bash
git clone https://github.com/inddigo/laboratorio2.git
cd laboratorio2
```

### Windows — PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows — Símbolo del sistema (CMD)

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para verificar que el entorno virtual está activo:

```bash
python -m pip --version
```

El comando debe mostrar una ruta relacionada con `.venv`. El archivo `.gitignore` excluye el entorno virtual y los archivos temporales. Puede comprobarse con `git status`.

## 4. Orden de ejecución

Una vez creado y activado el entorno virtual, desde la carpeta raíz del proyecto ejecutar, en este orden:

```bash
python scraper.py
python procesamiento.py
python buscador.py
```

- **`scraper.py`:** realiza una solicitud a la primera página del catálogo y muestra la cantidad total de libros y los primeros cinco registros.
- **`procesamiento.py`:** limpia los registros, calcula indicadores y genera o actualiza `libros.csv`.
- **`buscador.py`:** solicita una palabra o título, y muestra hasta cinco coincidencias de similitud positiva, de mayor a menor relevancia.

Para ejecutar varias búsquedas, volver a iniciar `python buscador.py` e ingresar una consulta diferente.

## 5. Extracción de datos (`scraper.py`)

Se utiliza `requests.get(URL, timeout=10)` junto con `raise_for_status()` para descargar y comprobar la respuesta HTTP, y `BeautifulSoup(..., "html.parser")` para analizar el HTML.

Cada libro se obtiene desde `article.product_pod`, extrayendo los siguientes campos:

| Campo | Elemento HTML | Transformación |
|---|---|---|
| `titulo` | Atributo `title` de `h3 a` | Se conserva el título completo. |
| `precio` | `p.price_color` | Se quita `£` y se convierte a `float`. |
| `disponibilidad` | `p.instock.availability` | Se extrae y limpia el texto. |
| `calificacion` | Clases de `p.star-rating` | `One` a `Five` se convierte a entero entre 1 y 5. |

**Manejo de datos faltantes:** cuando falta un selector, el campo queda en `None` en lugar de provocar una excepción. Si el precio no se puede convertir, también queda en `None`. Ante un error inesperado en un libro, se informa y se continúa procesando los demás. La función `obtener_libros()` no se ejecuta automáticamente al importar `scraper.py`, gracias a `if __name__ == "__main__":`.

## 6. Procesamiento y estructuración (`procesamiento.py`)

Los datos se convierten en un `DataFrame` de Pandas. El proceso contempla:

1. Quitar espacios sobrantes en los textos.
2. Eliminar registros duplicados según `titulo`.
3. Crear `titulo_normalizado` en minúsculas.
4. Convertir `precio` a tipo numérico (`float64`) y `calificacion` a tipo entero anulable (`Int64`).
5. Calcular la cantidad de libros y el precio promedio.
6. Exportar `libros.csv` con codificación UTF-8, sin índice.

### Evidencias obtenidas

| Indicador | Resultado registrado |
|---|---:|
| Libros extraídos | **20** |
| Precio promedio | **£38.05** |

Columnas del archivo CSV: `titulo`, `precio`, `disponibilidad`, `calificacion` y `titulo_normalizado`.

## 7. Recuperación de información (`buscador.py`)

El buscador lee `libros.csv`, descarta títulos normalizados vacíos y crea un índice con `TfidfVectorizer`. Cada consulta se transforma usando el mismo vocabulario del índice. Después se calcula la similitud del coseno para ordenar los resultados de mayor a menor, mostrando como máximo cinco títulos con puntuación positiva.

### Ejemplo 1: consulta `life`

```text
Scott Pilgrim's Precious Little Life (Scott Pilgrim #1) | Precio: 52.29 | Similitud: 0.2459
The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull | Precio: 17.93 | Similitud: 0.2250
Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991 | Precio: 57.25 | Similitud: 0.2231
```

### Ejemplo 2: consulta `secrets`

```text
The Dirty Little Secrets of Getting Your Dream Job | Precio: 33.34 | Similitud: 0.3672
```

**Comparación:** `life` aparece en tres títulos, por lo que su IDF es menor y las coincidencias de esa palabra tienen menor peso relativo; además, los títulos largos reparten el peso entre más términos. El título de Scott Pilgrim aparece primero según las puntuaciones registradas. `secrets` aparece en un solo título y alcanza una similitud mayor (0.3672) en ese resultado.

**Desafío `top_k=3`:** según las pruebas realizadas, `buscar("the", top_k=3)` devolvió tres resultados, mientras que `buscar("the")` devolvió cinco. Con `top_k=3` el límite es de tres resultados con similitud positiva.

## 8. Validación: pruebas funcionales

Se documentaron las cuatro pruebas solicitadas en la pauta, utilizando el buscador y el archivo CSV generado.

| Caso | Consulta utilizada | Resultado observado | Estado |
|---|---|---|---|
| **T1** | `life` | Tres libros con similitud positiva, ordenados de mayor a menor: 0.2459, 0.2250 y 0.2231. | **Cumple** |
| **T2** | `zzxyz123` | Se mostró «No se encontraron coincidencias.». | **Cumple** |
| **T3** | `LIFE` | Se obtuvieron los mismos tres libros, en el mismo orden y con las mismas puntuaciones que T1. | **Cumple** |
| **T4** | Consulta vacía (Enter) | Se mostró «Ingrese una consulta no vacia.» y después «No se encontraron coincidencias.», sin excepción. | **Cumple** |

**Observación de T4:** aparecen dos mensajes porque `buscar()` informa que la consulta está vacía y el bloque principal también indica que no hay coincidencias al recibir una lista vacía. Esto no impide cumplir el caso evaluado. Como mejora, se podría validar la entrada antes de llamar a `buscar()` y mostrar un solo aviso. La tabla refleja el comportamiento observado en la versión documentada.

## 9. Respuestas a las preguntas evaluadas

### Pregunta 1. ¿Para qué sirve BeautifulSoup y cómo se diferencia de requests?

`requests` realiza la petición HTTP y entrega la respuesta del servidor, incluyendo el código de estado y el HTML. `BeautifulSoup` analiza ese HTML y permite recorrer su estructura y seleccionar etiquetas, atributos y textos. Por lo tanto, `requests` obtiene el contenido y `BeautifulSoup` permite extraer la información que interesa.

### Pregunta 2. ¿Qué riesgo existe al depender de selectores HTML específicos si el sitio cambia?

Si el sitio modifica sus clases, etiquetas o estructura, los selectores podrían dejar de encontrar los datos correctos. El programa podría fallar o registrar valores vacíos o incorrectos. Para reducir el riesgo se deben manejar campos faltantes, revisar los datos extraídos y preferir selectores estables.

### Pregunta 3. ¿Por qué normalizar los títulos antes de implementar la búsqueda?

Normalizar evita que diferencias de mayúsculas, minúsculas o espacios afecten las coincidencias. Por ejemplo, `Life`, `LIFE` y `life` deben tratarse como la misma palabra. Esto mantiene el vocabulario consistente y permite comparar las consultas con los títulos de forma uniforme.

### Pregunta 4. ¿Qué hace `fit_transform()` sobre los títulos y por qué se usa `transform()` en la consulta?

`fit_transform()` aprende el vocabulario y los pesos IDF de los títulos, y convierte cada título en un vector TF-IDF para construir el índice. En cambio, `transform()` procesa una consulta nueva utilizando el vocabulario y los pesos ya aprendidos. Así se pueden comparar correctamente los vectores de la consulta con los títulos del índice.

### Pregunta 5. Si dos libros obtienen similitudes de 0.75 y 0.20 para la misma consulta, ¿cuál se muestra primero? ¿Qué indica una puntuación cercana a cero?

Se muestra primero el libro con similitud **0.75**, porque los resultados se ordenan de mayor a menor puntuación. Una puntuación cercana a cero indica muy poca coincidencia entre los términos de la consulta y los del título. Una similitud igual a cero significa que no hay coincidencias de términos representados en el vocabulario; el buscador no muestra esos resultados.

### Pregunta 6. ¿Qué limitación tiene buscar solo por palabras presentes en los títulos mediante TF-IDF? Proponga una mejora concreta.

El buscador depende de los términos presentes en los títulos y no comprende el significado de las palabras. Por ejemplo, una búsqueda de `music` puede no encontrar un libro sobre música si su título no contiene esa palabra. Tampoco reconoce necesariamente variantes como `secret` y `secrets`.

Una mejora concreta sería utilizar **lematización o stemming** para relacionar variantes de una palabra. También se podría emplear `TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))` para admitir coincidencias parciales y tolerar algunos errores de escritura. Una ampliación posterior sería indexar las descripciones de los libros o incorporar búsqueda semántica.

## 10. Entrega y reproducibilidad

El repositorio contiene los archivos requeridos para reproducir la solución. Para hacerlo desde cero, se deben seguir los pasos de las secciones **3** y **4**: clonar el repositorio, crear y activar `.venv`, instalar `requirements.txt` y ejecutar `scraper.py`, `procesamiento.py` y `buscador.py`, en ese orden.

**Nota:** las métricas, los ejemplos y los resultados de pruebas corresponden a la ejecución documentada. Si el catálogo web cambia, los registros o las puntuaciones podrían variar.
