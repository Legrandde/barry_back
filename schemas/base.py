from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints, create_model
from pydantic.alias_generators import to_camel


def _validate_safe_url(value: str) -> str:
    """Interdit les schémas dangereux (javascript:, vbscript:, data:) dans les liens."""
    lowered = value.strip().lower()
    if lowered.startswith(("javascript:", "vbscript:", "data:")):
        raise ValueError("Schéma d'URL interdit.")
    return value


# Types de champs réutilisables
RequiredText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=5000)]
# Chemin relatif (ex: "barry.png", servi par le site) ou URL absolue (média téléversé)
MediaPath = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500), AfterValidator(_validate_safe_url)]
SafeUrl = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500), AfterValidator(_validate_safe_url)]
Position = Annotated[int, Field(ge=0)]


class CamelModel(BaseModel):
    """Modèle de base : JSON en camelCase (comme le front React), Python en snake_case."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
        extra="forbid",
    )


def partial_model(model: type[CamelModel], name: str) -> type[CamelModel]:
    """Construit une variante du modèle où tous les champs sont optionnels (pour les PATCH)."""
    fields = {}
    for field_name, info in model.model_fields.items():
        annotation = Annotated[(info.annotation, *info.metadata)] if info.metadata else info.annotation
        fields[field_name] = (Optional[annotation], None)
    return create_model(name, __base__=CamelModel, **fields)


class ReorderRequest(CamelModel):
    """Liste complète des identifiants dans le nouvel ordre d'affichage."""

    ids: list[int] = Field(min_length=1)
