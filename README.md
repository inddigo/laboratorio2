# Laboratorio 2 — Scraping, procesamiento y buscador TF-IDF

**Integrantes:** Fernando Figueroa, German Oses , Joshua Villavicencio
**Repositorio:** https://github.com/inddigo/laboratorio2

Fuente: https://books.toscrape.com/ (solo la primera página, sin paginación).

## 1. Entorno virtual

Creación:

```bash
python -m venv .venv          # Windows: py -m venv .venv
```

Activación:

```bash
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (CMD)
.venv\Scripts\activate.bat
```

Instalación desde requirements.txt:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`.venv/` está en `.gitignore` y no se versiona (`git status` no lo muestra).

## 2. Orden de ejecución (desde un entorno nuevo)

```bash
git clone <URL del repositorio> && cd laboratorio2
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python scraper.py         # muestra total extraído y primeros 5 registros
python procesamiento.py   # limpia los datos y genera libros.csv
python buscador.py        # pide una consulta y muestra hasta 5 resultados
```

## 3. Extracción (scraper.py)

- `requests.get(URL, timeout=10)` + `raise_for_status()`; el HTML se analiza con `BeautifulSoup(..., "html.parser")`.
- Cada libro es un `article.product_pod`:
  - título: atributo `title` de `h3 a` (el texto visible viene truncado con "...");
  - precio: `p.price_color`, se quita el símbolo `£` y se convierte a `float`;
  - disponibilidad: `p.instock.availability`;
  - calificación: segunda clase de `p.star-rating` (`One`…`Five`) → entero 1–5.
- **Elementos sin datos:** si falta un selector el campo queda en `None` en lugar de lanzar excepción; si un precio no se puede convertir también queda `None`. Si un artículo provoca un error inesperado, se imprime un aviso y se continúa con los demás. `obtener_libros()` solo se ejecuta bajo `if __name__ == "__main__"`, por lo que importar el módulo no hace scraping.

## 4. Procesamiento (procesamiento.py)

DataFrame → `strip()` de textos → `drop_duplicates(subset="titulo")` → `titulo_normalizado` en minúsculas → `pd.to_numeric` para `precio` (float64) y `calificacion` (Int64) → `libros.csv` sin índice, UTF-8.

### Evidencias

| Indicador | Valor |
|---|---|
| Libros extraídos | **20** |
| Precio promedio | **£38.05** |

Columnas del CSV: `titulo, precio, disponibilidad, calificacion, titulo_normalizado`.

## 5. Ejemplos de búsqueda

**Consulta 1: `life`**

```
Scott Pilgrim's Precious Little Life (Scott Pilgrim #1) | Precio: 52.29 | Similitud: 0.2459
The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull | Precio: 17.93 | Similitud: 0.2250
Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991 | Precio: 57.25 | Similitud: 0.2231
```

**Consulta 2: `secrets`**

```
The Dirty Little Secrets of Getting Your Dream Job | Precio: 33.34 | Similitud: 0.3672
```

**Comparación:** "life" aparece en tres títulos, así que su IDF es menor y cada coincidencia pesa menos; además los tres títulos son largos, lo que diluye el peso del término. El de Scott Pilgrim queda primero porque es el más corto en términos distintos. "secrets" aparece en un solo título, tiene IDF alto y por eso logra una similitud mayor (0.3672) con un único resultado.

**Desafío `top_k=3`:** `buscar("the", top_k=3)` devolvió 3 resultados, mientras que `buscar("the")` devolvió 5. Nunca se superan tres y todos tienen similitud positiva.

## 6. Pruebas funcionales

| Caso | Consulta utilizada | Resultado observado | Estado |
|---|---|---|---|
| T1 | `life` | 3 libros con similitud positiva en orden descendente (0.2459, 0.2250, 0.2231). | Cumple |
| T2 | `zzxyz123` | Se mostró «No se encontraron coincidencias.» | Cumple |
| T3 | `LIFE` | Mismos 3 libros, mismo orden y mismas puntuaciones que T1 (la consulta se pasa a minúsculas). | Cumple |
| T4 | _(vacía)_ | Se mostró «Ingrese una consulta no vacia.» y luego «No se encontraron coincidencias.»; sin excepción. | Cumple |

Problema detectado: en T4 aparecen dos mensajes seguidos porque `buscar()` informa la consulta vacía y el bloque principal también imprime "sin coincidencias" al recibir una lista vacía. No es un error, pero se podría evitar validando la consulta antes de llamar a `buscar()`.

## 7. Respuestas

**Pregunta 1. ¿Para qué sirve BeautifulSoup y en qué se diferencia de requests?**
`requests` hace la petición HTTP y entrega la respuesta (código de estado, cabeceras y el HTML como texto). BeautifulSoup no descarga nada: toma ese HTML y lo convierte en un árbol de elementos que se puede recorrer y consultar con selectores (`select`, `find`) para extraer textos y atributos. Uno obtiene la página; el otro la interpreta.

**Pregunta 2. ¿Qué riesgo existe al depender de selectores HTML específicos si el sitio cambia?**
Si el sitio cambia de clases, etiquetas o estructura (por ejemplo, `price_color` pasa a llamarse distinto), los selectores dejan de encontrar elementos: el scraper puede fallar o, peor, seguir funcionando pero guardando campos vacíos o erróneos sin avisar. Para mitigarlo conviene usar selectores lo más estables posible, manejar los `None` y validar los datos (contar nulos, revisar que el total sea el esperado).

**Pregunta 3. ¿Por qué normalizar los títulos antes de implementar la búsqueda?**
Para que variaciones de forma no cuenten como palabras distintas: "Life", "LIFE" y "life" deben ser el mismo término. Al pasar a minúsculas y quitar espacios sobrantes, el vocabulario queda consistente y la consulta (que también se pasa a minúsculas) coincide con los títulos; eso es lo que hace que T3 cumpla.

**Pregunta 4. ¿Qué hace `fit_transform()` sobre los títulos y por qué se usa `transform()` en la consulta?**
`fit_transform()` aprende el vocabulario y los IDF a partir de todos los títulos (`fit`) y, a la vez, convierte cada título en su vector TF-IDF (`transform`), formando la matriz del índice. La consulta usa solo `transform()` para representarse con ese mismo vocabulario y los mismos pesos; si se volviera a ajustar con la consulta, el espacio vectorial cambiaría y los vectores no serían comparables con la matriz.

**Pregunta 5. Con similitudes 0.75 y 0.20, ¿cuál se muestra primero? ¿Qué indica una puntuación cercana a cero?**
Primero el de 0.75, porque los resultados se ordenan de mayor a menor similitud. Una puntuación cercana a cero indica que la consulta y el título casi no comparten términos (o comparten solo términos muy comunes y de bajo peso); en 0 exacto no comparten ninguno y el programa no lo muestra.

**Pregunta 6. ¿Qué limitación tiene buscar solo por palabras presentes en los títulos con TF-IDF? Proponga una mejora.**
Solo encuentra coincidencias exactas de palabras: no reconoce sinónimos ni significado ("music" no encuentra "Our Band Could Be Your Life"), tampoco variantes como "secret" frente a "secrets", y los títulos son textos muy cortos. Mejora concreta: aplicar lematización o stemming (por ejemplo con NLTK) para unificar singular/plural, y/o usar `TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))` para tolerar variantes y errores de tipeo. Una mejora mayor sería indexar también la descripción de cada libro o usar embeddings semánticos.
