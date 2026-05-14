# -*- coding: utf-8 -*-
"""
Created on Wed May 13 11:49:54 2026

@author: calex
"""

import streamlit as st
from utils.sheets import cargar_preguntas, obtener_materias
from utils.calificar import calificar_examen
from utils.reporte import generar_reporte
from utils.resultados import guardar_resultado
from datetime import datetime

st.set_page_config(page_title="Examen", page_icon="📝")

# Inicializar estado
if "enviado" not in st.session_state:
    st.session_state.enviado = False

# ── PANTALLA DEL EXAMEN ──
if not st.session_state.enviado:
    st.title("📝 Examen")

    nombre = st.text_input("Nombre completo")
    materia = st.selectbox("Materia", obtener_materias())

    if nombre and materia:
        # ✅ Solo carga las preguntas una vez
        clave = f"preguntas_{nombre}_{materia}"
        if clave not in st.session_state:
            st.session_state[clave] = cargar_preguntas(materia)
   
        preguntas = st.session_state[clave]
        respuestas = {}

        st.markdown("---")
        for i, row in preguntas.iterrows():
            st.markdown(f"*{i+1}. {row['pregunta']}*")

            if str(row['tipo']).strip().lower() == 'multiple':
                opciones = []
                for letra, col in zip(['A','B','C','D'], ['opcion_a','opcion_b','opcion_c','opcion_d']):
                    if row.get(col):
                        opciones.append(f"{letra}) {row[col]}")

                seleccion = st.radio("Selecciona tu respuesta:", opciones, key=f"q_{i}", index=None, label_visibility="collapsed")
                if seleccion:
                    respuestas[i] = seleccion[0]  # Solo la letra A/B/C/D
            else:
                respuesta = st.text_area("Tu respuesta:", key=f"q_{i}")
                if respuesta:
                    respuestas[i] = respuesta

            st.markdown("---")

        if st.button("📨 Entregar examen", type="primary"):
            if len(respuestas) < len(preguntas):
                st.warning("⚠️ Por favor responde todas las preguntas antes de entregar.")
            else:
                try:
                    resultado = calificar_examen(preguntas, respuestas)
                    doc_bytes = generar_reporte(nombre, materia, resultado, preguntas)
                    st.write("✅ Reporte generado")  # debug

                    nombre_archivo = f"{nombre}{materia}{datetime.now().strftime('%d%m%Y_%H%M')}.docx"
                    st.write(f"📤 Subiendo archivo: {nombre_archivo}")  # debug
                    try:
                        guardar_resultado(nombre, materia, resultado)
                        st.session_state.error_sheets=None
                        st.write("✅ Respuestas guardadas")  # debug
                    except Exception as e:
                        st.session_state.error_sheets=f"❌ Error exacto: {type(e).__name__}: {e}"

                    st.session_state.enviado = True
                    st.session_state.resultado = resultado
                    st.session_state.doc_bytes = doc_bytes
                    st.session_state.nombre = nombre
                    st.session_state.materia = materia
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {e}")  # ← esto mostrará el error exacto
                
                
                resultado = calificar_examen(preguntas, respuestas)
                doc_bytes = generar_reporte(nombre, materia, resultado, preguntas)


# ── PANTALLA DE RESULTADOS ──
else:
    resultado = st.session_state.resultado
    st.title("✅ Examen entregado")
    st.success(f"¡Gracias, *{st.session_state.nombre}*! Tu examen fue recibido.")

    col1, col2 = st.columns(2)
    col1.metric("Puntos obtenidos", resultado['calificacion'])
    col2.metric("Total posible", resultado['total'])

    st.info("Las preguntas abiertas serán revisadas por tu profesor.")

    st.download_button(
        label="📄 Descargar mi reporte",
        data=st.session_state.doc_bytes,
        file_name=f"reporte_{st.session_state.nombre}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
