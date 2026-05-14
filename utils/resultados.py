# -*- coding: utf-8 -*-
"""
Created on Wed May 13 18:18:39 2026

@author: calex
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def guardar_resultado(nombre, materia, resultado):
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
    except FileNotFoundError:
        import streamlit as st
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)

    sheet = cliente.open("Examenes").worksheet("Resultados")

    # Armar resumen de respuestas
    detalle = ""
    for i, d in enumerate(resultado['detalles']):
        if d['tipo'] == 'multiple':
            estado = "✅" if d['correcto'] else "❌"
            detalle += f"P{i+1}: {estado} ({d['respuesta_alumno']}) | "
        else:
            detalle += f"P{i+1}: [Abierta: {d['respuesta_alumno'][:30]}...] | "

    # Agregar fila
    sheet.append_row([
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        nombre,
        materia,
        resultado['calificacion'],
        resultado['total'],
        detalle
    ])
