from app.core.database import Base, engine
from app.models import Workspace, Document


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    init_database()
