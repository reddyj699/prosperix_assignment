from pydantic import BaseModel, Field

class SKUModel(BaseModel):
    sku: str = Field(min_length=3, max_length=20, pattern="^[a-zA-Z0-9]+$")
