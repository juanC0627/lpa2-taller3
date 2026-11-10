from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from musica_api.database import get_session
from musica_api.models import Favorito, FavoritoCreate, Usuario, Cancion

router = APIRouter()

@router.get("", response_model=List[Favorito])
def listar_favoritos(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    """Paginación incluida (Sugerencia de Mejora #2)"""
    return session.exec(select(Favorito).offset(offset).limit(limit)).all()

@router.post("", response_model=Favorito, status_code=201)
def marcar_favorito(favorito: FavoritoCreate, session: Session = Depends(get_session)):
    if not session.get(Usuario, favorito.id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not session.get(Cancion, favorito.id_cancion):
        raise HTTPException(status_code=404, detail="Canción no encontrada")
        
    existente = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == favorito.id_usuario,
            Favorito.id_cancion == favorito.id_cancion
        )
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="La canción ya está en favoritos del usuario")

    nuevo_favorito = Favorito.model_validate(favorito)
    session.add(nuevo_favorito)
    session.commit()
    session.refresh(nuevo_favorito)
    return nuevo_favorito

@router.get("/{id}", response_model=Favorito)
def obtener_favorito(id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, id)
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    return favorito

@router.delete("/{id}")
def eliminar_favorito(id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, id)
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado")
    session.delete(favorito)
    session.commit()
    return {"ok": True, "message": "Favorito eliminado correctamente"}