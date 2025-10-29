from __future__ import annotations
from pathlib import Path
from typing import Literal
from pynigeria.exceptions import NotFoundError
from pynigeria.loader import DataLoader
from pynigeria.models import LGA, Settlement, State


class Nigeria:
    """
    Main entry point for accessing Nigerian geographic data.

    Example:
        >>> nigeria = Nigeria()
        >>> state = nigeria.get_state("Lagos")
        >>> print(state.capital)
        'Ikeja'

        >>> settlement = nigeria.get_settlement("Kontagora")
        >>> print(settlement.state_code)
        'NG-NI'
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        """
        Initialize the Nigeria data interface.

        Args:
            data_dir: Optional custom data directory. Defaults to package data.
        """

        self._loader = DataLoader(data_dir)

        # Lazy-loaded data
        self._states: list[State] | None = None
        self._lgas: list[LGA] | None = None
        self._settlements: list[Settlement] | None = None

        # Lazy-loaded indices
        self._state_by_code: dict[str, State] | None = None
        self._state_by_name: dict[str, State] | None = None
        self._lga_by_state: dict[str, list[LGA]] | None = None
        self._settlement_by_name: dict[str, Settlement] | None = None
        self._settlement_by_state: dict[str, list[Settlement]] | None = None

    # ========================================================================
    # Data Access (with lazy loading)
    # ========================================================================

    def states(self) -> list[State]:
        """
        Get all Nigerian states.

        Returns:
            List of all states. Data is loaded and cached on first call.
        """

        if self._states is None:
            self._states = self._loader.load_states()
            self._build_state_indices()
        return self._states

    def lgas(self) -> list[LGA]:
        """
        Get all Local Government Areas.

        Returns:
            List of all LGAs. Data is loaded and cached on first call.
        """

        if self._lgas is None:
            self._lgas = self._loader.load_lgas()
            self._build_lga_indices()
        return self._lgas

    def settlements(self) -> list[Settlement]:
        """
        Get all settlements (cities, towns, villages).

        Returns:
            List of all settlements. Data is loaded and cached on first call.
        """

        if self._settlements is None:
            self._settlements = self._loader.load_settlements()
            self._build_settlement_indices()
        return self._settlements

    # ========================================================================
    # Query Methods - States
    # ========================================================================

    def get_state(self, name: str) -> State:
        """
        Get a state by its name (case-insensitive).

        Args:
            name: State name (e.g., "Lagos", "Kano")

        Returns:
            The matching State object

        Raises:
            NotFoundError: If state is not found
        """

        if self._state_by_name is None:
            self.states()  # Load data and build indices

        name_key = name.lower().strip()
        if name_key not in self._state_by_name:
            raise NotFoundError(f"State not found: {name}")

        return self._state_by_name[name_key]

    def get_state_by_code(self, code: str) -> State:
        """
        Get a state by its ISO code.

        Args:
            code: ISO 3166-2 state code (e.g., "NG-LA" for Lagos)

        Returns:
            The matching State object

        Raises:
            NotFoundError: If state code is not found
        """

        if self._state_by_code is None:
            self.states()  # Load data and build indices

        code_upper = code.upper().strip()
        if code_upper not in self._state_by_code:
            raise NotFoundError(f"State code not found: {code}")

        return self._state_by_code[code_upper]

    def get_state_capital(self, name: str) -> str:
        """
        Get the capital city of a state by its name.

        Args:
            name: State name (e.g., "Lagos", "Kano")

        Returns:
            The capital city of the state

        Raises:
            NotFoundError: If state is not found
        """

        state = self.get_state(name)
        return state.capital

    # ========================================================================
    # Query Methods - LGAs
    # ========================================================================

    def get_lgas(
        self,
        state_code: str | None = None,
        state_name: str | None = None,
    ) -> list[LGA]:
        """
        Get LGAs, optionally filtered by state.

        Args:
            state_code: Filter by state code (e.g., "NG-LA")
            state_name: Filter by state name (e.g., "Lagos")

        Returns:
            List of matching LGAs

        Raises:
            NotFoundError: If specified state is not found

        Example:
            >>> nigeria = Nigeria()
            >>> lagos_lgas = nigeria.get_lgas(state_name="Lagos")
            >>> len(lagos_lgas)
            20
        """

        if self._lgas is None:
            self.lgas()  # Load data

        # No filter - return all
        if state_code is None and state_name is None:
            return self._lgas

        # Get state code from name if needed
        if state_name is not None:
            state = self.get_state(state_name)
            state_code = state.code

        # Filter by state code
        if state_code is not None:
            if self._lga_by_state is None:
                self._build_lga_indices()

            state_code_upper = state_code.upper().strip()
            if state_code_upper not in self._lga_by_state:
                return []

            return self._lga_by_state[state_code_upper]

        return self._lgas

    def get_lga(self, name: str, state_code: str | None = None) -> LGA:
        """
        Get a specific LGA by name.

        Args:
            name: LGA name
            state_code: Optional state code to narrow search

        Returns:
            The matching LGA object

        Raises:
            NotFoundError: If LGA is not found
        """
        lgas = self.get_lgas(state_code=state_code)
        name_lower = name.lower().strip()

        for lga in lgas:
            if lga.name.lower() == name_lower:
                return lga

        raise NotFoundError(f"LGA not found: {name}")

    # ========================================================================
    # Query Methods - Settlements
    # ========================================================================

    def get_settlement(self, name: str) -> Settlement:
        """
        Get a settlement by its name (case-insensitive).

        Args:
            name: Settlement name (e.g., "Kontagora", "Ibadan")

        Returns:
            The matching Settlement object

        Raises:
            NotFoundError: If settlement is not found
        """

        if self._settlement_by_name is None:
            self.settlements()  # Load data and build indices

        name_key = name.lower().strip()
        if name_key not in self._settlement_by_name:
            raise NotFoundError(f"Settlement not found: {name}")

        return self._settlement_by_name[name_key]

    def get_settlements(
        self,
        state_code: str | None = None,
        state_name: str | None = None,
        settlement_type: Literal["city", "town", "village"] | None = None,
    ) -> list[Settlement]:
        """
        Get settlements, optionally filtered.

        Args:
            state_code: Filter by state code
            state_name: Filter by state name
            settlement_type: Filter by type (city, town, or village)

        Returns:
            List of matching settlements

        Example:
            >>> nigeria = Nigeria()
            >>> cities = nigeria.get_settlements(
            ...     state_name="Lagos",
            ...     settlement_type="city"
            ... )
        """
        if self._settlements is None:
            self.settlements()  # Load data

        results = self._settlements

        # Filter by state
        if state_name is not None:
            state = self.get_state(state_name)
            state_code = state.code

        if state_code is not None:
            if self._settlement_by_state is None:
                self._build_settlement_indices()

            state_code_upper = state_code.upper().strip()
            results = self._settlement_by_state.get(state_code_upper, [])

        # Filter by type
        if settlement_type is not None:
            results = [s for s in results if s.type == settlement_type]

        return results

    def search_settlements(self, query: str) -> list[Settlement]:
        """
        Search settlements by name substring (case-insensitive).

        Args:
            query: Substring to search for in settlement names

        Returns:
            List of matching settlements
        """
        if self._settlements is None:
            self.settlements()  # Load data

        query_lower = query.lower().strip()
        results = [s for s in self._settlements if query_lower in s.name.lower()]

        return results


    def _build_state_indices(self) -> None:
        """Build lookup indices for states."""
        if self._states is None:
            return

        self._state_by_code = {s.code.upper(): s for s in self._states}
        self._state_by_name = {s.name.lower(): s for s in self._states}

    def _build_lga_indices(self) -> None:
        """Build lookup indices for LGAs."""
        if self._lgas is None:
            return

        self._lga_by_state = {}
        for lga in self._lgas:
            state_code = lga.state_code.upper()
            if state_code not in self._lga_by_state:
                self._lga_by_state[state_code] = []
            self._lga_by_state[state_code].append(lga)

    def _build_settlement_indices(self) -> None:
        """Build lookup indices for settlements."""
        if self._settlements is None:
            return

        self._settlement_by_name = {s.name.lower(): s for s in self._settlements}
        self._settlement_by_state = {}

        for settlement in self._settlements:
            state_code = settlement.state_code.upper()
            if state_code not in self._settlement_by_state:
                self._settlement_by_state[state_code] = []
            self._settlement_by_state[state_code].append(settlement)
