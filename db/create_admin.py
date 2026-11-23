"""Crée un compte admin, ou change le mot de passe d'un compte existant.

Le mot de passe est saisi au clavier, masqué : il n'apparaît jamais dans le code, dans Git
ni dans l'historique du terminal.

Usage, depuis barry_back/ :
    uv run python -m db.create_admin               # demande l'identifiant puis le mot de passe
    uv run python -m db.create_admin barry         # identifiant donné, mot de passe demandé
"""

import sys
from getpass import getpass

from sqlalchemy import select

from core.security import hash_password
from db.session import SessionLocal
from models import Admin

# Même règle que le changement de mot de passe depuis l'espace admin
MIN_PASSWORD_LENGTH = 8


def ask_password() -> str:
    while True:
        password = getpass("Mot de passe : ")
        if len(password) < MIN_PASSWORD_LENGTH:
            print(f"Au moins {MIN_PASSWORD_LENGTH} caractères.")
        elif getpass("Confirmez le mot de passe : ") != password:
            print("Les deux saisies sont différentes.")
        else:
            return password


def main() -> None:
    username = (sys.argv[1] if len(sys.argv) > 1 else input("Identifiant : ")).strip()
    if not username:
        sys.exit("Identifiant vide : rien n'a été fait.")
    password = ask_password()

    with SessionLocal() as db:
        admin = db.scalar(select(Admin).where(Admin.username == username))
        if admin is None:
            db.add(Admin(username=username, hashed_password=hash_password(password)))
            result = "créé"
        else:
            admin.hashed_password = hash_password(password)
            result = "existait déjà, mot de passe changé"
        db.commit()

    print(f"Compte « {username} » : {result}.")


if __name__ == "__main__":
    main()
