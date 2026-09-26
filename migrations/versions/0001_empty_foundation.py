"""Establish the empty foundation migration chain.

Revision ID: 0001_empty_foundation
Revises:
"""

from typing import Sequence


revision: str = "0001_empty_foundation"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Reserve the first revision without introducing application tables."""


def downgrade() -> None:
    """The empty foundation revision has no schema changes to reverse."""
