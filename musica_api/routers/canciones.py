from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from musica_api.database import get_session
from musica_api.models import Cancion, CancionCreate, CancionUpdate
from utils import validar_año

router = APIRouter()

@router.get("/buscar", response_model=List[Cancion])
def buscar_canciones(
    titulo: Optional[str] = None,
    artista: Optional[str] = None,
    genero: Optional[str] = None,
    session: Session = Depends(get_session)
):
    query = select(Cancion)
    if titulo:
        query = query.where(Cancion.titulo.contains(titulo))
    if artista:
        query = query.where(Cancion.artista.contains(artista))
    if genero:
        query = query.where(Cancion.genero.contains(genero))
    return session.exec(query).all()

@router.get("", response_model=List[Cancion])
def listar_canciones(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    """Paginación incluida (Sugerencia de Mejora #2)"""
    return session.exec(select(Cancion).offset(offset).limit(limit)).all()

@router.post("", response_model=Cancion, status_code=201)
def crear_cancion(cancion: CancionCreate, session: Session = Depends(get_session)):
    if not validar_año(cancion.año):
        raise HTTPException(status_code=400, detail="Año de lanzamiento inválido")
    nueva_cancion = Cancion.model_validate(cancion)
    session.add(nueva_cancion)
    session.commit()
    session.refresh(nueva_cancion)
    return nueva_cancion

@router.get("/{id}", response_model=Cancion)
def obtener_cancion(id: int, session: Session = Depends(get_session)):
    cancion = session.get(Cancion, id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return cancion

@router.put("/{id}", response_model=Cancion)
def actualizar_cancion(id: int, cancion_data: CancionUpdate, session: Session = Depends(get_session)):
    cancion = session.get(Cancion, id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    
    data = cancion_data.model_dump(exclude_unset=True)
    if "año" in data and data["año"]:
        if not validar_año(data["año"]):
            raise HTTPException(status_code=400, detail="Año de lanzamiento inválido")
            
    for key, value in data.items():
        setattr(cancion, key, value)
        
    session.add(cancion)
    session.commit()
    session.refresh(cancion)
    return cancion

@router.delete("/{id}")
def eliminar_cancion(id: int, session: Session = Depends(get_session)):
    cancion = session.get(Cancion, id)
    if not cancion:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    session.delete(cancion)
    session.commit()
    return {"ok": True, "message": "Canción eliminada correctamente"}