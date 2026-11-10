from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from musica_api.database import get_session
from musica_api.models import Usuario, UsuarioCreate, UsuarioUpdate
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