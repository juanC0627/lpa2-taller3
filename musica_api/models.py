from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class UsuarioBase(SQLModel):
    nombre: str
    correo: str = Field(unique=True, index=True)

class Usuario(UsuarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_registro: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioUpdate(SQLModel):
    nombre: Optional[str] = None
    correo: Optional[str] = None


class CancionBase(SQLModel):
    titulo: str = Field(index=True)
    artista: str = Field(index=True)
    album: str
    duracion: int
    año: int
    genero: str = Field(index=True)

class Cancion(CancionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_creacion: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

class CancionCreate(CancionBase):
    pass

class CancionUpdate(SQLModel):
    titulo: Optional[str] = None
    artista: Optional[str] = None
    album: Optional[str] = None
    duracion: Optional[int] = None
    año: Optional[int] = None
    genero: Optional[str] = None


class FavoritoBase(SQLModel):
    id_usuario: int = Field(foreign_key="usuario.id")
    id_cancion: int = Field(foreign_key="cancion.id")

class Favorito(FavoritoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_marcado: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

class FavoritoCreate(FavoritoBase):
    pass