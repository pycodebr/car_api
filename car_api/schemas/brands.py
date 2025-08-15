from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class BrandSchema(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

    @field_validator('name')
    def name_min_length(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Nome da marca deve ter pelo menos 2 caracteres')
        return v.strip()


class BrandUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator('name')
    def name_min_length(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Nome da marca deve ter pelo menos 2 caracteres')
        return v.strip() if v is not None else v


class BrandPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]


class BrandListPublicSchema(BaseModel):
    brands: List[BrandPublicSchema]
    offset: int
    limit: int
