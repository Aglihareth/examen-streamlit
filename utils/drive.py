# -*- coding: utf-8 -*-
"""
Created on Wed May 13 14:27:52 2026

@author: calex
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from io import BytesIO

CARPETA_ID = "1OiaK_yveczLLOuaqMaYY5V7bws3isrWS"

def subir_a_drive(nombre_archivo, doc_bytes, nombre_carpeta="Examenes"):
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("credenciales.json", scopes=scopes)
    servicio = build("drive", "v3", credentials=creds)

    metadata = {
        "name": nombre_archivo,
        "parents": [CARPETA_ID]  # ← sube directo a tu carpeta
    }
    media = MediaIoBaseUpload(
        BytesIO(doc_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    servicio.files().create(
        body=metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True
    ).execute()

    # Buscar o crear la carpeta
    carpeta_id = _obtener_carpeta(servicio, nombre_carpeta)

    # Subir el archivo
    metadata = {
        "name": nombre_archivo,
        "parents": [carpeta_id]
    }
    media = MediaIoBaseUpload(
        BytesIO(doc_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    servicio.files().create(
        body=metadata,
        media_body=media,
        fields="id"
    ).execute()

def _obtener_carpeta(servicio, nombre_carpeta):
    # Busca si ya existe la carpeta
    resultado = servicio.files().list(
        q=f"name='{nombre_carpeta}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        fields="files(id)"
    ).execute()

    archivos = resultado.get("files", [])
    if archivos:
        return archivos[0]["id"]

    # Si no existe, la crea
    carpeta = servicio.files().create(
        body={
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder"
        },
        fields="id"
    ).execute()
    return carpeta["id"]