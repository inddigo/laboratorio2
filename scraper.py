"""Extracción de libros de la primera página de https://books.toscrape.com/."""
import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/"
ESTRELLAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def convertir_precio(texto):
    """'£51.77' -> 51.77. Devuelve None si no se puede convertir."""
    limpio = "".join(c for c in texto if c.isdigit() or c == ".")
    try:
        return float(limpio)
    except ValueError:
        return None


def extraer_libro(articulo):
    """Extrae los cuatro campos de un <article class="product_pod">.
    Si falta algún elemento, el campo queda en None y no se detiene la ejecución."""
    enlace = articulo.select_one("h3 a")
    precio = articulo.select_one("p.price_color")
    disponibilidad = articulo.select_one("p.instock.availability")
    estrellas = articulo.select_one("p.star-rating")

    calificacion = None
    if estrellas:
        for clase in estrellas.get("class", []):
            if clase in ESTRELLAS:
                calificacion = ESTRELLAS[clase]

    return {
        # El texto visible del <a> viene truncado ("..."); el atributo title trae el título completo.
        "titulo": enlace.get("title", enlace.get_text()).strip() if enlace else None,
        "precio": convertir_precio(precio.get_text()) if precio else None,
        "disponibilidad": disponibilidad.get_text(strip=True) if disponibilidad else None,
        "calificacion": calificacion,
    }


def obtener_libros(url=URL):
    respuesta = requests.get(url, timeout=10)
    respuesta.raise_for_status()
    respuesta.encoding = "utf-8"
    soup = BeautifulSoup(respuesta.text, "html.parser")

    libros = []
    for articulo in soup.select("article.product_pod"):
        try:
            libros.append(extraer_libro(articulo))
        except Exception as error:  # un libro mal formado no detiene el resto
            print(f"Aviso: se omitió un libro por error: {error}")
    return libros


if __name__ == "__main__":
    libros = obtener_libros()
    print(f"Total de libros extraídos: {len(libros)}")
    for libro in libros[:5]:
        print(libro)
