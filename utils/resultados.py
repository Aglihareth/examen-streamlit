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
    import streamlit as st
    
    cliente = _get_cliente()
    st.write("✅ Cliente conectado")
    
    sheet = cliente.open("ExamenStreamlit").worksheet("Resultados")
    st.write(f"✅ Hoja encontrada: {sheet.title}")

    detalle = ""
    for i, d in enumerate(resultado['detalles']):
        if d['tipo'] == 'multiple':
            estado = "✅" if d['correcto'] else "❌"
            detalle += f"P{i+1}: {estado} ({d['respuesta_alumno']}) | "
        else:
            if st.session_stage.get("error_sheets"):
                st.error(f"error guardar en Sheets: {st.session_state.error_sheets}")
            Resultado = st.session_state.resultado
            detalle += f"P{i+1}: [Abierta: {d['respuesta_alumno'][:30]}...] | "

    fila = [
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        nombre,
        materia,
        resultado['calificacion'],
        resultado['total'],
        detalle
    ]
    st.write(f"📝 Datos a escribir: {fila}")  # ← ver qué se intenta guardar
    
    sheet.append_row(fila, value_input_option='USER_ENTERED')
    st.write("✅ Fila agregada")
