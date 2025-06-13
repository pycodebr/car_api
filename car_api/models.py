# from sqlalchemy import Column, Integer, String, Text
# from sqlalchemy.orm import declarative_base

# Base = declarative_base()


# class Car(Base):
#     __tablename__ = 'cars'

#     id = Column(Integer, primary_key=True, index=True)
#     brand = Column(String, nullable=False)
#     model = Column(String, nullable=False)
#     color = Column(String, nullable=True)
#     factory_year = Column(Integer, nullable=True)
#     model_year = Column(Integer, nullable=True)
#     description = Column(Text, nullable=True)


from typing import Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Car:
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=None
    )
    factory_year: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None
    )
    model_year: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None
    )
