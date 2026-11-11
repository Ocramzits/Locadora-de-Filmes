import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.database import Base, SessionLocal, engine
from backend.models_db import ClienteDB, FilmeDB, LocacaoDB
from models.cliente import clientes_iniciais
from models.filme import filmes_iniciais


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(ClienteDB).count() == 0:
            for nome in clientes_iniciais():
                cliente = ClienteDB(nome=nome)
                db.add(cliente)
            db.commit()

        if db.query(FilmeDB).count() == 0:
            for item in filmes_iniciais():
                filme = FilmeDB(
                    titulo=item["titulo"],
                    categoria=item["categoria"],
                    copias=item["copias"],
                    total_copias=item["total_copias"],
                    disponivel=item["disponivel"],
                )
                db.add(filme)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
