from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from musica_api.database import get_session
from musica_api.models import Usuario, UsuarioCreate, UsuarioUpdate, Favorito, Cancion
from utils import validar_correo

router = APIRouter()

@router.get("", response_model=List[Usuario])
def listar_usuarios(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    """Paginación incluida (Sugerencia de Mejora #2)"""
    return session.exec(select(Usuario).offset(offset).limit(limit)).all()

@router.post("", response_model=Usuario, status_code=201)
def crear_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    if not validar_correo(usuario.correo):
        raise HTTPException(status_code=400, detail="Correo electrónico inválido")
    
    db_usuario = session.exec(select(Usuario).where(Usuario.correo == usuario.correo)).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
        
    nuevo_usuario = Usuario.model_validate(usuario)
    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario

@router.get("/{id}", response_model=Usuario)
def obtener_usuario(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{id}", response_model=Usuario)
def actualizar_usuario(id: int, usuario_data: UsuarioUpdate, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    data = usuario_data.model_dump(exclude_unset=True)
    if "correo" in data and data["correo"]:
        if not validar_correo(data["correo"]):
            raise HTTPException(status_code=400, detail="Correo electrónico inválido")
            
    for key, value in data.items():
        setattr(usuario, key, value)
        
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.delete("/{id}")
def eliminar_usuario(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()
    return {"ok": True, "message": "Usuario eliminado correctamente"}


# =============================================================================
# ENDPOINTS DE FAVORITOS POR USUARIO (Integración con Frontend Taller #4)
# =============================================================================

@router.get("/{id}/favoritos", response_model=List[Cancion])
def listar_favoritos_usuario(id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    query = (
        select(Cancion)
        .join(Favorito, Favorito.id_cancion == Cancion.id)
        .where(Favorito.id_usuario == id)
    )
    return session.exec(query).all()


@router.post("/{id_usuario}/favoritos/{id_cancion}", response_model=Favorito, status_code=201)
def marcar_favorito_usuario(id_usuario: int, id_cancion: int, session: Session = Depends(get_session)):
    if not session.get(Usuario, id_usuario):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not session.get(Cancion, id_cancion):
        raise HTTPException(status_code=404, detail="Canción no encontrada")

    existente = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == id_usuario,
            Favorito.id_cancion == id_cancion
        )
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="La canción ya está en favoritos del usuario")

    nuevo_favorito = Favorito(id_usuario=id_usuario, id_cancion=id_cancion)
    session.add(nuevo_favorito)
    session.commit()
    session.refresh(nuevo_favorito)
    return nuevo_favorito


@router.delete("/{id_usuario}/favoritos/{id_cancion}")
def eliminar_favorito_usuario(id_usuario: int, id_cancion: int, session: Session = Depends(get_session)):
    favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == id_usuario,
            Favorito.id_cancion == id_cancion
        )
    ).first()
    if not favorito:
        raise HTTPException(status_code=404, detail="Favorito no encontrado para este usuario")

    session.delete(favorito)
    session.commit()
    return {"ok": True, "message": "Favorito eliminado del usuario"}