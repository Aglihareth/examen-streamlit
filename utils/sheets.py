# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:10:54 2026

@author: calex
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import random
import streamlit as st
import time

@st.cache_resource
def _get_cliente():
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file(
            "credenciales.json", scopes=scopes
        )
    except FileNotFoundError:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=scopes
        )
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def obtener_materias():
    cliente = _get_cliente()
    sheet = cliente.open("ExamenStreamlit")
    hojas_excluidas = ["Resultados"]
    return [ws.title for ws in sheet.worksheets()
            if ws.title not in hojas_excluidas]

@st.cache_data(ttl=300)  # ← datos crudos cacheados para TODOS los alumnos
def _cargar_datos_raw(materia):
    for intento in range(3):  # 3 reintentos si falla
        try:
            cliente = _get_cliente()
            sheet = cliente.open("ExamenStreamlit").worksheet(materia)
            datos = sheet.get_all_records()
            return pd.DataFrame(datos)
        except Exception as e:
            if intento < 2:
                time.sleep(2 ** intento)  # espera 1s, 2s, 4s entre reintentos
            else:
                raise e

def cargar_preguntas(materia, num_preguntas=None):
    # Datos cacheados — solo 1 llamada a Google para todos
    df = _cargar_datos_raw(materia).copy()

    # Aleatorización individual por alumno — sin llamar a Google
    if num_preguntas and num_preguntas < len(df):
        df = df.sample(n=num_preguntas).reset_index(drop=True)
    else:
        df = df.sample(frac=1).reset_index(drop=True)

    for i, row in df.iterrows():
        if str(row['tipo']).strip().lower() == 'multiple':
            opciones = {
                'A': row['opcion_a'],
                'B': row['opcion_b'],
                'C': row['opcion_c'],
                'D': row['opcion_d']
            }
            clave = str(row['respuesta_correcta']).strip().upper()
            if clave not in opciones:
                continue
            correcta_texto = opciones[clave]
            items = list(opciones.values())
            random.shuffle(items)
            letras = ['A', 'B', 'C', 'D']
            for j, letra in enumerate(letras):
                df.at[i, f'opcion_{letra.lower()}'] = items[j]
            nueva_correcta = letras[items.index(correcta_texto)]
            df.at[i, 'respuesta_correcta'] = nueva_correcta

    return df
