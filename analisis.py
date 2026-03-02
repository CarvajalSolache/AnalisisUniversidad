import pandas as pd
import json
import os

# ==============================
# CONFIGURACIÓN
# ==============================

ARCHIVO_CSV = "datos_rendimiento_universidad.csv"
ARCHIVO_SALIDA = "datos_dashboard.json"
UMBRAL_REPROBACION = 6.0

# ==============================
# VALIDACIÓN INICIAL
# ==============================

if not os.path.exists(ARCHIVO_CSV):
    raise FileNotFoundError(f"No se encontró el archivo '{ARCHIVO_CSV}'.")

df = pd.read_csv(ARCHIVO_CSV)

COLUMNAS_REQUERIDAS = {
    "id_estudiante",
    "carrera",
    "materia",
    "calificacion",
    "semestre",
    "año"
}

if not COLUMNAS_REQUERIDAS.issubset(df.columns):
    raise ValueError("El CSV no tiene las columnas necesarias.")

# ==============================
# FUNCIONES DE ANÁLISIS
# ==============================

def calcular_kpis():
    promedio_general = round(df["calificacion"].mean(), 2)

    tasa_reprobacion = round(
        (len(df[df["calificacion"] < UMBRAL_REPROBACION]) / len(df)) * 100,
        2
    )

    promedio_estudiante = df.groupby("id_estudiante")["calificacion"].mean()
    alumnos_en_riesgo = int((promedio_estudiante < UMBRAL_REPROBACION).sum())

    return {
        "promedio_general": promedio_general,
        "tasa_reprobacion": tasa_reprobacion,
        "alumnos_en_riesgo": alumnos_en_riesgo
    }


def materias_mayor_reprobacion():
    total = df.groupby("materia")["calificacion"].count()
    reprobados = df[df["calificacion"] < UMBRAL_REPROBACION]
    reprobados_m = reprobados.groupby("materia")["calificacion"].count()

    tasa = ((reprobados_m / total) * 100).fillna(0)
    tasa = tasa.sort_values(ascending=False)

    return [
        {
            "materia": materia,
            "tasa_reprobacion": round(porcentaje, 2)
        }
        for materia, porcentaje in tasa.items()
    ]


def carreras_con_mayor_promedio():
    promedio = (
        df.groupby("carrera")["calificacion"]
        .mean()
        .sort_values(ascending=False)
    )

    return [
        {
            "carrera": carrera,
            "promedio": round(prom, 2)
        }
        for carrera, prom in promedio.items()
    ]


def tendencias_por_semestre():
    promedio = (
        df.groupby(["año", "semestre"])["calificacion"]
        .mean()
        .reset_index()
        .sort_values(["año", "semestre"])
    )

    return [
        {
            "año": int(row["año"]),
            "semestre": int(row["semestre"]),
            "promedio": round(row["calificacion"], 2)
        }
        for _, row in promedio.iterrows()
    ]


def detectar_riesgo_academico():
    promedio_estudiante = df.groupby("id_estudiante")["calificacion"].mean()
    riesgo_ids = promedio_estudiante[promedio_estudiante < UMBRAL_REPROBACION].index

    detalle = df[
        (df["id_estudiante"].isin(riesgo_ids)) &
        (df["calificacion"] < UMBRAL_REPROBACION)
    ]

    return detalle[[
        "id_estudiante",
        "carrera",
        "materia",
        "calificacion",
        "semestre",
        "año"
    ]].to_dict(orient="records")


# ==============================
# GENERAR JSON FINAL
# ==============================

dashboard_data = {
    "kpis": calcular_kpis(),
    "materias_reprobacion": materias_mayor_reprobacion(),
    "carreras_promedio": carreras_con_mayor_promedio(),
    "tendencias_semestre": tendencias_por_semestre(),
    "alumnos_riesgo": detectar_riesgo_academico()
}

with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, indent=4, ensure_ascii=False)

print(f"Archivo '{ARCHIVO_SALIDA}' generado correctamente.")