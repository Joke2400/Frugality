"""Contains a store class that keeps track of a state as well as store data."""

from dataclasses import dataclass, field
from typing import Any, Optional

from utils import OneOfType
from utils import Found
from utils import NotFound
from utils import ParseFailed
from utils import QueryPending


@dataclass
class Store:
    """Class that stores a name, id and slug for a store.

    The class also stores a state that is managed by a type-validator
    descriptor. State is intended to be used for match/if statements
    as a clean way to do control flow through type-checking.

    The core idea is to enable structural pattern matching to be used on a
    class in a way where the type of a single field determines what should
    be done with the data stored in other fields in that instance.

    For example:

    match store.state:

        case Found():
            # Do something

        case NotFound()
            # Do something else

    Is the syntax i wanted to enable with this class. Since store name and id
    values can either be the name and id of a Store() that was Found(), or
    the name and id of a query(Store) that was NotFound(), keeping track
    of state in this way enables a cleaner syntax whilst enabling a
    more varied sort of control flow throughout the program. It's also
    more clear what's going on than it is when you're just using tuples.

    For greater performance, the descriptor validator could be dropped, as it's
    not strictly necessary for the class to work. It's been implemented to
    require that the coder (me) models possible states more rigidly/clearly.
    """

    name: Optional[str] = None
    store_id: Optional[str] = None
    slug: Optional[str] = None
    state: Any = field(
        default=OneOfType(
            Found,
            NotFound,
            QueryPending,
            ParseFailed),
        repr=False)

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
