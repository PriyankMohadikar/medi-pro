"""
SQLAlchemy ORM models for the Healthcare Pricing database.

Defines four tables:
  - providers       : Healthcare providers and competitors
  - test_pricing    : Individual test prices per provider
  - package_pricing : Health check-up packages per provider
  - package_tests   : Individual tests included in each package
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
    provider_name = Column(Text, nullable=False, index=True)
    provider_type = Column(Text, nullable=True)
    city = Column(Text, nullable=True, index=True)
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
    ES Price and Competitor Price from Excel are stored as
    separate rows with their respective provider references.
    """

    __tablename__ = "test_pricing"

    pricing_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(
        Integer, ForeignKey("providers.provider_id"), nullable=True
    )
    test_name = Column(Text, nullable=True, index=True)
    category = Column(Text, nullable=True, index=True)
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
    Individual tests within the package are stored in package_tests.
    """

    __tablename__ = "package_pricing"

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(
        Integer, ForeignKey("providers.provider_id"), nullable=True
    )
    package_name = Column(Text, nullable=True, index=True)
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

    Stores one row per test per package, created by splitting
    the comma-separated 'Tests Included' column from Excel.
    """

    __tablename__ = "package_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(
        Integer, ForeignKey("package_pricing.package_id"), nullable=True
    )
    test_name = Column(Text, nullable=True, index=True)

    # Relationships
    package = relationship("PackagePricing", back_populates="tests")

    def __repr__(self) -> str:
        return f"<PackageTest(id={self.id}, test='{self.test_name}')>"


class TestCost(Base):
    """
    Internal processing cost for a diagnostic test.

    Stores the actual lab/operational cost for each test, used for
    profitability analysis and pricing optimization. One entry per
    unique test_name (matches test_pricing.test_name).
    """

    __tablename__ = "test_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(Text, nullable=False, unique=True, index=True)
    cost_price = Column(Numeric(10, 2), nullable=False)

    def __repr__(self) -> str:
        return f"<TestCost(id={self.id}, test='{self.test_name}', cost={self.cost_price})>"


class CustomPackage(Base):
    """
    User-created custom healthcare package.

    Stores package configuration and computed pricing fields.
    Package names must be unique across all custom packages.
    """

    __tablename__ = "custom_packages"

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    package_name = Column(Text, nullable=False, unique=True, index=True)
    total_tests = Column(Integer, nullable=True)
    individual_total_price = Column(Numeric(10, 2), nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    suggested_package_price = Column(Numeric(10, 2), nullable=True)
    market_average_price = Column(Numeric(10, 2), nullable=True)
    expected_customer_savings = Column(Numeric(10, 2), nullable=True)
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
    tests = relationship(
        "CustomPackageTest",
        back_populates="package",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CustomPackage(id={self.package_id}, name='{self.package_name}')>"


class CustomPackageTest(Base):
    """
    Individual test included in a user-created custom package.

    Stores the test name, its individual price at time of inclusion,
    and display order for consistent rendering.
    """

    __tablename__ = "custom_package_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(
        Integer,
        ForeignKey("custom_packages.package_id", ondelete="CASCADE"),
        nullable=False,
    )
    test_name = Column(Text, nullable=False)
    individual_price = Column(Numeric(10, 2), nullable=True)
    display_order = Column(Integer, nullable=True)

    # Relationships
    package = relationship("CustomPackage", back_populates="tests")

    def __repr__(self) -> str:
        return f"<CustomPackageTest(id={self.id}, test='{self.test_name}')>"
