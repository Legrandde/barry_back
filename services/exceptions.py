from typing import Any


class ServiceError(Exception):
    """Erreur métier, convertie en réponse HTTP par le gestionnaire déclaré dans main.py."""

    status_code = 400

    def __init__(self, detail: Any):
        super().__init__(detail)
        self.detail = detail


class NotFoundError(ServiceError):
    status_code = 404


class ConflictError(ServiceError):
    status_code = 409


class InvalidDataError(ServiceError):
    status_code = 422


class PayloadTooLargeError(ServiceError):
    status_code = 413


class UnsupportedMediaError(ServiceError):
    status_code = 415
