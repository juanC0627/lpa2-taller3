"""
Módulo de utilidades para la aplicación.
Contiene funciones auxiliares utilizadas en diferentes partes de la aplicación.
"""
import re
from datetime import datetime

def validar_correo(correo: str) -> bool:
    """
    Valida que un correo electrónico tenga un formato válido.
    
    Args:
        correo (str): Correo electrónico a validar
        
    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, correo))

def formatear_duracion(segundos: int) -> str:
    """
    Convierte una duración en segundos a formato mm:ss.
    
    Args:
        segundos (int): Duración en segundos
        
    Returns:
        str: Duración formateada como mm:ss
    """
    minutos = segundos // 60
    segs_restantes = segundos % 60
    return f"{minutos:02d}:{segs_restantes:02d}"

def generar_slug(texto: str) -> str:
    """
    Genera un slug a partir de un texto.
    Un slug es una versión de texto amigable para URLs.
    
    Args:
        texto (str): Texto a convertir en slug
        
    Returns:
        str: Slug generado
    """
    slug = texto.lower()
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug

def obtener_año_actual() -> int:
    """
    Obtiene el año actual.
    
    Returns:
        int: Año actual
    """
    return datetime.now().year

def validar_año(año: int) -> bool:
    """
    Valida que un año sea válido (no futuro y no muy antiguo).
    
    Args:
        año (int): Año a validar
        
    Returns:
        bool: True si el año es válido, False en caso contrario
    """
    año_actual = obtener_año_actual()
    return 1900 <= año <= año_actual