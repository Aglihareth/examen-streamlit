# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:10:54 2026

@author: calex
"""

import pandas as pd
import random

ARCHIVO = "preguntas.xlsx"

def obtener_materias():
    xl = pd.ExcelFile(ARCHIVO)
    return xl.sheet_names

def cargar_preguntas(materia, num_preguntas=None):
    df = pd.read_excel(ARCHIVO, sheet_name=materia)

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
