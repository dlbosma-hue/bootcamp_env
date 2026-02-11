"""Pydantic data models for the Product Description Generator."""

from typing import List

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    features: List[str] = Field(default_factory=list)

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
