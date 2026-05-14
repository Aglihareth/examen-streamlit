# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:48:23 2026

@author: calex
"""

from docxtpl import DocxTemplate
from io import BytesIO
from datetime import datetime

def generar_reporte(nombre, materia, resultado, preguntas_df):
    import streamlit as st
    st.write("usando reporte con machote")
    
    doc = DocxTemplate("machote.docx")

    # Calcular porcentaje
    if resultado['total'] > 0:
        porcentaje = round((resultado['calificacion'] / resultado['total']) * 100, 1)
    else:
        porcentaje = 0

    # Preparar datos de cada pregunta
    preguntas_contexto = []
    for i, d in enumerate(resultado['detalles']):
        pregunta = preguntas_df.iloc[i]

        if d['tipo'] == 'multiple':
            # Encontrar el texto de la respuesta del alumno
            letra = str(d['respuesta_alumno']).upper()
            col_map = {'A': 'opcion_a', 'B': 'opcion_b', 
                      'C': 'opcion_c', 'D': 'opcion_d'}
            texto_resp = pregunta.get(col_map.get(letra, 'opcion_a'), '')

            estado = "✅ Correcto" if d['correcto'] else f"❌ Incorrecto (correcta: {d['respuesta_correcta']})"
            puntos = d['puntos']
        else:
            texto_resp = ""
            estado = "⏳ Pendiente de revisión"
            puntos = 0

        preguntas_contexto.append({
            'numero': i + 1,
            'pregunta': d['pregunta'],
            'tipo': d['tipo'],
            'opcion_a': pregunta.get('opcion_a', ''),
            'opcion_b': pregunta.get('opcion_b', ''),
            'opcion_c': pregunta.get('opcion_c', ''),
            'opcion_d': pregunta.get('opcion_d', ''),
            'respuesta_alumno': d['respuesta_alumno'],
            'texto_respuesta': texto_resp,
            'respuesta_correcta': d.get('respuesta_correcta', ''),
            'estado': estado,
            'puntos': puntos,
            'puntos_posibles': d['puntos_posibles']
        })

    # Contexto completo para el machote
    contexto = {
        'nombre': nombre,
        'materia': materia,
        'fecha': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'calificacion': resultado['calificacion'],
        'total': resultado['total'],
        'porcentaje': porcentaje,
        'preguntas': preguntas_contexto
    }

    doc.render(contexto)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
