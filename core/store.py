"""Contains a store class that keeps track of a state as well as store data."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Store:
    """Dataclass for storing store data."""

    name: Optional[str] = None
    store_id: Optional[str] = None
    slug: Optional[str] = None

    @property
    def data(self) -> tuple[str | None, str | None, str | None]:
        """Return store fields as a tuple of strings (name, id, slug)."""
        return (self.name, self.store_id, self.slug)

    def set_fields(self, name: str, sid: str, slug: str) -> None:
        """Set fields to given values."""
        self.name = name
        self.store_id = sid
        self.slug = slug

    def __str__(self) -> str:
        """Return human-readable string containing store name and id."""
        return f"<Store: '{self.name}', '{self.store_id}'>"
