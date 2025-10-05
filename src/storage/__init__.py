"""
Storage layer for Kira Prolongation Support application.
Provides SQLite database persistence.
"""
from .data_store import DataStore, DatabaseError

__all__ = ["DataStore", "DatabaseError"]

