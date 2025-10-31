from datetime import datetime
import re
import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .base import TimestampMixin, PaginationResultSchema
from ..enums import Race

class CharacterBaseSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=21, description="Name of the character")
    user_id: uuid.UUID = Field(..., description="ID of the user who owns the character")
    location_slug: Optional[str] = Field(None, description="Location of the character")
    is_male: bool = Field(..., description="Gender of the character")
    race: Race = Field(..., description="Race of the character")
    level: int = Field(..., description="Level of the character")
    experience: int = Field(..., description="Experience points of the character")
    health: int = Field(..., description="Health points of the character")
    max_health: int = Field(..., description="Max health points of the character")
    tiredness: float = Field(..., description="Tiredness points of the character")
    tiredness: float = Field(..., description="Max tiredness points of the character")
    endurance: int = Field(..., description="Endurance points of the character")
    mana: int = Field(..., description="Mana points of the character")
    max_mana: int = Field(..., description="Max mana points of the character")
    intelligence: int = Field(..., description="Intelligence points of the character")
    gold: float = Field(..., description="Gold owned by the character")
    ducats: float = Field(..., description="Ducats owned by the character")
    power: int = Field(..., description="Power of the character")
    agility: int = Field(..., description="Agility of the character")
    lucky: int = Field(..., description="Luck of the character")
    is_main: bool = Field(..., description="Is the character the main character?")
    photo_id: uuid.UUID = Field(..., description="ID of the photo character")
    is_online: bool = Field(False, description="Status of character")
    is_active: bool = Field(True, description="Is the character active?")
    deactivated_at: Optional[datetime] = Field(None, description="Timestamp when the character was deactivated")
    scheduled_deletion_at: Optional[datetime] = Field(None, description="Timestamp when the character is scheduled for deletion")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        # Проверка длины
        if len(v) < 2 or len(v) > 21:
            raise ValueError('Name must be more 2 characters and no more than 21 characters long')
        
        # Проверка на пустоту (с учетом пробелов)
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        
        # Проверка на допустимые символы (добавлен пробел)
        if not re.match(r'^[a-zA-Z0-9 ]+$|^[а-яА-ЯёЁ0-9 ]+$', v):
            raise ValueError('Name must contain only letters of one language (Russian or English), numbers and spaces')
        
        # Проверка, что все буквы одного языка
        has_cyrillic = bool(re.search(r'[а-яА-ЯёЁ]', v))
        has_latin = bool(re.search(r'[a-zA-Z]', v))
        
        if has_cyrillic and has_latin:
            raise ValueError('Name must contain letters of only one language (Russian or English)')
        
        # Проверка на пробелы в начале/конце
        if v != v.strip():
            raise ValueError('Name cannot start or end with a space')
        
        # Проверка на множественные пробелы подряд
        if '  ' in v:
            raise ValueError('Name cannot contain multiple consecutive spaces')
        
        return v


class CharacterMultCreateSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the character")
    race: Race = Field(..., description="Race of the character")
    is_male: bool = Field(..., description="Gender of the character")


class CharacterCreateSchema(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the character")
    user_id: uuid.UUID = Field(..., description="ID of the user who owns the character")
    race: Race = Field(..., description="Race of the character")
    is_male: bool = Field(..., description="Gender of the character")
    referral_code: Optional[str] = Field(None, description="Referral code for the character")

class CharacterReadSchema(CharacterBaseSchema, TimestampMixin):
    id: uuid.UUID = Field(..., description="Unique identifier of the character")

class CharacterUpdateSchema(CharacterBaseSchema):
    pass

class CharacterSimpleReadSchema(TimestampMixin):
    id: uuid.UUID = Field(..., description="Unique identifier of the character")
    name: str = Field(..., max_length=100, description="Name of the character")
    user_id: uuid.UUID = Field(..., description="ID of the user who owns the character")
    is_main: bool = Field(..., description="Is the character the main character?")
    is_online: bool = Field(False, description="Status of character")


class CharacterSimpleListReadSchema(BaseModel):
    characters: list[CharacterSimpleReadSchema] = Field(..., description="List of simple character data")

class CharacterListIds(BaseModel):
    ids: list[uuid.UUID] = Field(..., description="List of character IDs")

class UserListids(BaseModel):
    ids: list[uuid.UUID] = Field(..., description="List of user IDs")


class CharacterSimpleInfoReadSchema(TimestampMixin):
    id: uuid.UUID = Field(..., description="Unique identifier of the character")
    name: str = Field(..., max_length=100, description="Name of the character")
    is_male: bool = Field(..., description="Gender of character")
    race: Race = Field(..., description="Race of character")
    level: int = Field(..., description="Level of character")
    is_online: bool = Field(False, description="Status of character")
    location_slug: Optional[str] = Field(None, description="Location of the character")

class CharacterSimpleInfoListReadSchema(BaseModel):
    characters: list[CharacterSimpleInfoReadSchema]

class PaginationCharacterSimpleInfoReadSchema(PaginationResultSchema[CharacterSimpleInfoReadSchema]):
    pass

class CharacterOnlineStatus(BaseModel):
    is_online: bool