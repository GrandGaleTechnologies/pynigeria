from __future__ import annotations
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

