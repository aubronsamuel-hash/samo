from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Equipment, EquipmentStatus, Event, EventStatus, User


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def test_organization():
    return uuid4()


@pytest.fixture(scope="function")
def test_manager(db_session, test_organization):
    manager = User(
        email="manager@example.com",
        roles=["manager"],
        organization_id=test_organization,
        first_name="Casey",
        last_name="Manager",
    )
    db_session.add(manager)
    db_session.commit()
    db_session.refresh(manager)
    return manager


@pytest.fixture(scope="function")
def test_technician(db_session, test_organization):
    technician = User(
        email="tech@example.com",
        roles=["technician"],
        organization_id=test_organization,
        first_name="Taylor",
        last_name="Tech",
    )
    db_session.add(technician)
    db_session.commit()
    db_session.refresh(technician)
    return technician


@pytest.fixture(scope="function")
def test_event(db_session, test_manager):
    event = Event(
        name="Festival Jazz 2024",
        description="Production principale",
        start_date=date(2024, 2, 15),
        end_date=date(2024, 2, 16),
        venue={"name": "Main Stage", "address": "1 Rue du Jazz"},
        technical_requirements={},
        budget={},
        status=EventStatus.CONFIRMED,
        created_by=test_manager.id,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture(scope="function")
def test_equipment(db_session, test_manager):
    equipment = Equipment(
        name="Console Son",
        category="audio",
        subcategory="mixing_console",
        status=EquipmentStatus.AVAILABLE,
        quantity=1,
        organization_id=test_manager.organization_id,
    )
    db_session.add(equipment)
    db_session.commit()
    db_session.refresh(equipment)
    return equipment


@pytest.fixture(scope="function")
def authorized_client(db_session, test_manager):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.headers.update(
            {"Authorization": f"Bearer mock:{test_manager.email}"}
        )
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(authorized_client):
    return authorized_client
