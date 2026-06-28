# Author: Ck.epsilon & Chaos (AI Programming Assistant)
"""Scrapy Item definitions — validated with Pydantic schemas."""

import scrapy
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ScrapedItemSchema(BaseModel):
    """Pydantic schema for scraped item validation.

    Each spider defines its own fields; this is the base contract
    that all scraped items must satisfy.
    """

    url: str = Field(..., description="Source URL where this item was found")
    title: Optional[str] = Field(None, description="Item title or name")
    scraped_at: str = Field(..., description="ISO 8601 timestamp of extraction")

    @field_validator("url")
    @classmethod
    def url_must_be_http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://, got: {v}")
        return v.strip()

    class Config:
        extra = "allow"  # Spiders can add arbitrary fields


class GenericItem(scrapy.Item):
    """Dynamic Scrapy Item — fields defined at runtime from spider config."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fields will be populated by the spider based on YAML config
