from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime, String

from portfolio_backend.db.base import Base


class TextDataModel(Base):
    """SQLAlchemy model class representing textual data.

    Attributes:
        __tablename__ (str): The name of the database table for textual data.
        text_id (Mapped[str]): Primary key identifier for each text data entry.
        filename (Mapped[str]): Name of the file associated with the text data.
        text (Mapped[str]): The textual content itself.
        source (Mapped[str]): The source or origin of the text data.
        topic (Mapped[str]): The topic or category to which the text data relates.
        created_at (Mapped[datetime]): Timestamp indicating when the text data was created.

    """

    __tablename__ = "text_data"

    text_id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    topic: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
