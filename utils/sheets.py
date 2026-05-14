# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:10:54 2026

@author: calex
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import random

def _get_cliente():
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
    except FileNotFoundError:
        import streamlit as st
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
    return gspread.authorize(creds)

def obtener_materias():
    cliente = _get_cliente()
    sheet = cliente.open("Examenes")
    
    hojas_excluidas = ["Resultados"]
    
    return [ws.title for ws in sheet.worksheets()
            if ws.title not in hojas_excluidas]

def cargar_preguntas(materia, num_preguntas=None):
    cliente = _get_cliente()
    sheet = cliente.open("Examenes").worksheet(materia)
    datos = sheet.get_all_records()
    df = pd.DataFrame(datos)

    # 1️⃣ Seleccionar N preguntas aleatorias o mezclar todas
    if num_preguntas and num_preguntas < len(df):
        df = df.sample(n=num_preguntas).reset_index(drop=True)
    else:
        df = df.sample(frac=1).reset_index(drop=True)

    # 2️⃣ Mezclar opciones de preguntas múltiples
    for i, row in df.iterrows():
        if str(row['tipo']).strip().lower() == 'multiple':
            opciones = {
                'A': row['opcion_a'],
                'B': row['opcion_b'],
                'C': row['opcion_c'],
                'D': row['opcion_d']
            }
            correcta_texto = opciones[row['respuesta_correcta'].upper()]

            items = list(opciones.values())
            random.shuffle(items)

            letras = ['A', 'B', 'C', 'D']
            for j, letra in enumerate(letras):
                df.at[i, f'opcion_{letra.lower()}'] = items[j]

            nueva_correcta = letras[items.index(correcta_texto)]
            df.at[i, 'respuesta_correcta'] = nueva_correcta

    return df
