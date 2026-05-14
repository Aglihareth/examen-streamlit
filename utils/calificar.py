# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:46:01 2026

@author: calex
"""

def calificar_examen(preguntas, respuestas):
    puntos_obtenidos = 0
    puntos_totales = 0
    detalles = []

    for i, row in preguntas.iterrows():
        puntos = row['puntos']
        puntos_totales += puntos

        if str(row['tipo']).strip().lower() == 'multiple':
            correcta = str(row['respuesta_correcta']).upper().strip()
            dada = str(respuestas.get(i, '')).upper().strip()
            es_correcta = dada == correcta
            if es_correcta:
                puntos_obtenidos += puntos
            detalles.append({
                'pregunta': row['pregunta'],
                'tipo': 'multiple',
                'respuesta_alumno': respuestas.get(i, ''),
                'respuesta_correcta': correcta,
                'correcto': es_correcta,
                'puntos': puntos if es_correcta else 0,
                'puntos_posibles': puntos
            })
        else:
            detalles.append({
                'pregunta': row['pregunta'],
                'tipo': 'abierta',
                'respuesta_alumno': respuestas.get(i, ''),
                'respuesta_correcta': 'Revisión manual',
                'correcto': None,
                'puntos': 0,
                'puntos_posibles': puntos
            })

    return {
        'calificacion': puntos_obtenidos,
        'total': puntos_totales,
        'detalles': detalles
    }