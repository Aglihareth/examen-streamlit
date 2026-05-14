# -*- coding: utf-8 -*-
"""
Created on Wed May 13 18:18:39 2026

@author: calex
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def _get_cliente():
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    try:
        creds = Credentials.from_service_account_file(
            "credenciales.json", scopes=scopes
        )
    except FileNotFoundError:
        import streamlit as st
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=scopes
        )
    return gspread.authorize(creds)

def guardar_resultado(nombre, materia, resultado):
    cliente = _get_cliente()
    spreadsheet = cliente.open("Examenes")
    sheet = spreadsheet.worksheet("Resultados")

    detalle = ""
    for i, d in enumerate(resultado['detalles']):
        if d['tipo'] == 'multiple':
            estado = "SI" if d['correcto'] else "NO"
            detalle += f"P{i+1}:{estado}({d['respuesta_alumno']}) | "
        else:
            texto = str(d['respuesta_alumno'])[:30]
            detalle += f"P{i+1}:Abierta({texto}) | "

    fila = [
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        str(nombre),
        str(materia),
        int(resultado['calificacion']),
        int(resultado['total']),
        str(detalle)
    ]

    # Obtener siguiente fila vacía y escribir directamente
    siguiente_fila = len(sheet.get_all_values()) + 1
    rango = f"A{siguiente_fila}:F{siguiente_fila}"
    sheet.update(rango, [fila])
