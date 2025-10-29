from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


class State(BaseModel):
    """
    Represents a Nigerian state.

    Attributes:
        name: Full name of the state (e.g., "Lagos")
        code: ISO 3166-2 state code (e.g., "NG-LA")
        capital: State capital city
    """

    name: str = Field(..., min_length=1, description="State name")
    code: str = Field(..., pattern=r"^NG-[A-Z]{2}$", description="ISO state code")
    capital: str = Field(..., min_length=1, description="State capital")

    class Config:
        frozen = True  # Make immutable


class LGA(BaseModel):
    """
    Represents a Local Government Area.

    Attributes:
        name: Full name of the LGA
        code: Short code for the LGA (optional)
        state_code: Reference to parent state's code
    """

    name: str = Field(..., min_length=1, description="LGA name")
    code: str | None = Field(None, description="LGA code (if available)")
    state_code: str = Field(
        ..., pattern=r"^NG-[A-Z]{2}$", description="Parent state code"
    )

    class Config:
        frozen = True


class Settlement(BaseModel):
    """Represents a city, town, or village.

    Attributes:
        name: Settlement name
        type: Classification as city, town, or village
        lga: Name of parent LGA
        lga_code: Code of parent LGA (if available)
        state_code: Code of parent state
    """

    name: str = Field(..., min_length=1, description="Settlement name")
    type: Literal["city", "town", "village"] = Field(..., description="Settlement type")
    lga: str = Field(..., min_length=1, description="Parent LGA name")
    lga_code: str | None = Field(None, description="Parent LGA code")
    state_code: str = Field(
        ..., pattern=r"^NG-[A-Z]{2}$", description="Parent state code"
    )

    class Config:
        frozen = True
