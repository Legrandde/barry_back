"""Seeder de la base de données du portfolio d'Alhassane Barry.

Usage, depuis barry_back/ :
    uv run python -m db.seed           # remplit les sections manquantes et les collections si la base est vide
    uv run python -m db.seed --reset   # réinitialise les sections et collections (conserve les comptes admin)
"""

import argparse

from sqlalchemy import delete, func, select

import models  # noqa: F401
from core.config import settings
from db import seed_data
from db.base import Base
from db.init_db import add_missing_columns, seed_content
from db.session import SessionLocal, engine
from models import (
    Admin,
    Education,
    Experience,
    Project,
    Section,
    ServiceItem,
    SkillCategory,
    SocialLink,
    Testimonial,
)
from services.auth import ensure_admin


def run_seed(*, reset: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_columns()
    settings.media_dir.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as db:
        ensure_admin(db, settings.admin_username, settings.admin_password)

        if reset:
            for model in (
                Section,
                ServiceItem,
                SkillCategory,
                Experience,
                Education,
                Project,
                Testimonial,
                SocialLink,
            ):
                db.execute(delete(model))
            db.flush()

        seed_content(db)
        db.commit()

        counts = {
            "sections": db.scalar(select(func.count()).select_from(Section)) or 0,
            "projects": db.scalar(select(func.count()).select_from(Project)) or 0,
            "services": db.scalar(select(func.count()).select_from(ServiceItem)) or 0,
            "skill_categories": db.scalar(select(func.count()).select_from(SkillCategory)) or 0,
            "experiences": db.scalar(select(func.count()).select_from(Experience)) or 0,
            "educations": db.scalar(select(func.count()).select_from(Education)) or 0,
            "testimonials": db.scalar(select(func.count()).select_from(Testimonial)) or 0,
            "social_links": db.scalar(select(func.count()).select_from(SocialLink)) or 0,
            "admins": db.scalar(select(func.count()).select_from(Admin)) or 0,
        }

    mode = "réinitialisée et remplie" if reset else "vérifiée et remplie"
    print(f"Base de données {mode} ({settings.database_url}) :")
    for name, count in counts.items():
        print(f"  - {name}: {count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seeder du CMS portfolio d'Alhassane Barry")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vide les sections et collections avant de réinsérer les données initiales",
    )
    args = parser.parse_args()
    run_seed(reset=args.reset)


if __name__ == "__main__":
    main()
