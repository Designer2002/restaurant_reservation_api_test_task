from .tables import router as tables_router
from .reservations import router as reservations_router

__all__ = ["tables_router", "reservations_router"]