"""
SQLAlchemy ORM models for the Healthcare Pricing database.

Defines four tables (matching existing PostgreSQL schema):
  - providers       : Healthcare providers and competitors
  - test_pricing    : Individual test prices per provider
  - package_pricing : Health check-up packages per provider
  - package_tests   : Individual tests included in each package

IMPORTANT: These models REFLECT the existing database schema.
           DO NOT run Base.metadata.create_all() — the tables
           already exist and must not be modified.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Provider(Base):
    """
    Healthcare provider or diagnostic lab.

    Each provider is unique per (provider_name, city) combination,
    allowing the same chain to exist across multiple cities.
    """

    __tablename__ = "providers"

    provider_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(Text, nullable=False)
    provider_type = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    # Relationships
    test_prices = relationship(
        "TestPricing", back_populates="provider", cascade="all, delete-orphan"
    )
    packages = relationship(
        "PackagePricing", back_populates="provider", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("provider_name", "city", name="uq_provider_name_city"),
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.provider_id}, name='{self.provider_name}', city='{self.city}')>"


class TestPricing(Base):
    """
    Individual diagnostic test price for a specific provider.

    Each provider can have only one price per test_name.
    """

    __tablename__ = "test_pricing"

    pricing_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(
        Integer, ForeignKey("providers.provider_id"), nullable=True
    )
    test_name = Column(Text, nullable=True)
    category = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    # Relationships
    provider = relationship("Provider", back_populates="test_prices")

    __table_args__ = (
        UniqueConstraint("provider_id", "test_name", name="uq_provider_test"),
    )

    def __repr__(self) -> str:
        return f"<TestPricing(id={self.pricing_id}, test='{self.test_name}', price={self.price})>"


class PackagePricing(Base):
    """
    Health check-up package offered by a provider.

    Each provider can have only one entry per package_name.
    """

    __tablename__ = "package_pricing"

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(
        Integer, ForeignKey("providers.provider_id"), nullable=True
    )
    package_name = Column(Text, nullable=True)
    package_price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )

    # Relationships
    provider = relationship("Provider", back_populates="packages")
    tests = relationship(
        "PackageTest", back_populates="package", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "provider_id", "package_name", name="uq_provider_package"
        ),
    )

    def __repr__(self) -> str:
        return f"<PackagePricing(id={self.package_id}, name='{self.package_name}', price={self.package_price})>"


class PackageTest(Base):
    """
    Individual test included in a health check-up package.
    """

    __tablename__ = "package_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(
        Integer, ForeignKey("package_pricing.package_id"), nullable=True
    )
    test_name = Column(Text, nullable=True)

    # Relationships
    package = relationship("PackagePricing", back_populates="tests")

    def __repr__(self) -> str:
        return f"<PackageTest(id={self.id}, test='{self.test_name}')>"
