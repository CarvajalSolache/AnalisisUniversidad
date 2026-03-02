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

# Forzar tipos de datos
df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce")
df["semestre"] = pd.to_numeric(df["semestre"], errors="coerce")
df["año"] = pd.to_numeric(df["año"], errors="coerce")
df["id_estudiante"] = pd.to_numeric(df["id_estudiante"], errors="coerce")

# Columnas requeridas
COLUMNAS_REQUERIDAS = {"id_estudiante", "carrera", "materia", "calificacion", "semestre", "año"}
if not COLUMNAS_REQUERIDAS.issubset(df.columns):
    raise ValueError("El CSV no tiene las columnas necesarias.")

# ==============================
# FUNCIONES DE ANÁLISIS
# ==============================
def calcular_kpis():
    promedio_general = round(df["calificacion"].mean(), 2)
    tasa_reprobacion = round((df["calificacion"] < UMBRAL_REPROBACION).mean() * 100, 2)
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
    tasa = ((reprobados_m / total) * 100).fillna(0).sort_values(ascending=False)
    return [{"materia": m, "tasa_reprobacion": round(p, 2)} for m, p in tasa.items()]

def carreras_con_mayor_promedio():
    promedio = df.groupby("carrera")["calificacion"].mean().sort_values(ascending=False)
    return [{"carrera": c, "promedio": round(p,2)} for c, p in promedio.items()]

def tendencias_por_semestre():
    promedio = df.groupby(["año", "semestre"])["calificacion"].mean().reset_index().sort_values(["año", "semestre"])
    return [{"año": int(r["año"]), "semestre": int(r["semestre"]), "promedio": round(r["calificacion"], 2)} 
            for _, r in promedio.iterrows()]

# ==============================
# DETECTAR ALUMNOS EN RIESGO (SIMPLIFICADO)
# ==============================
def detectar_riesgo_academico():
    # Tomar todas las filas donde la calificación < UMBRAL_REPROBACION
    detalle = df[df["calificacion"] < UMBRAL_REPROBACION]
    
    # Ordenar por calificación ascendente para ver primero los más críticos
    detalle = detalle.sort_values(by="calificacion")
    
    # Convertir a lista de diccionarios
    return detalle[["id_estudiante","carrera","materia","calificacion","semestre","año"]].to_dict(orient="records")

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
# Verifica los tipos de columnas
print(df.dtypes)

# Asegúrate que calificacion sea float
df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce")

# Verifica cuántos alumnos en riesgo hay
print(df[df["calificacion"] < UMBRAL_REPROBACION])
with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    json.dump(dashboard_data, f, indent=4, ensure_ascii=False)

print(f"Archivo '{ARCHIVO_SALIDA}' generado correctamente.")