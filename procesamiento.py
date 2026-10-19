"""Limpieza y estructuración de los libros extraídos; exporta libros.csv."""
import pandas as pd
from scraper import obtener_libros

libros = obtener_libros()
df = pd.DataFrame(libros)

print(df.head())
print(df.info())
print(df.shape)
print(list(df.columns))

# Limpieza
df["titulo"] = df["titulo"].astype("string").str.strip()
df["disponibilidad"] = df["disponibilidad"].astype("string").str.strip()
df = df.drop_duplicates(subset="titulo").reset_index(drop=True)
df["titulo_normalizado"] = df["titulo"].str.lower()

# Tipos numéricos
df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce").astype("Int64")
print(df.dtypes)

# Indicadores
print(f"Cantidad de libros: {len(df)}")
print(f"Precio promedio: {df['precio'].mean():.2f}")

df.to_csv("libros.csv", index=False, encoding="utf-8")
print("Exportado libros.csv")
