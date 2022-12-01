# define Python user-defined exceptions
from pydantic import BaseModel


class Error(Exception):
    """Base class for other exceptions"""
    pass


class HTTPError(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "HTTPException raised."},
        }