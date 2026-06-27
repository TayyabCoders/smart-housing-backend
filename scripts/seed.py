"""
Database seeding script
Populates the database with sample data for development and testing
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from passlib.context import CryptContext

from app.configs.app_config import settings
from app.di.loader import load_all_dependencies
from app.di.container import container
from app.models.user_model import User, Role
from app.models.camera import Camera
from app.models.person import Person
from app.models.vehicle import Vehicle
from app.models.enums import CameraType, PersonRole, VehicleStatus

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


async def get_db_session():
    """Get database session from container"""
    database = container.resolve('database')
    await database.connect()
    return database.get_session(operation_type="write")


async def seed_users(session: AsyncSession):
    """Seed users table"""
    print("Seeding users...")
    
    # Check if users already exist
    result = await session.execute(text("SELECT COUNT(*) FROM users"))
    count = result.scalar()
    if count > 0:
        print(f"  Skipping - {count} users already exist")
        return
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@smarthousing.com",
            "hashed_password": hash_password("admin123"),
            "role": Role.admin,
            "is_active": True,
        },
        {
            "username": "security_manager",
            "email": "security@smarthousing.com",
            "hashed_password": hash_password("security123"),
            "role": Role.user,
            "is_active": True,
        },
        {
            "username": "resident1",
            "email": "resident1@smarthousing.com",
            "hashed_password": hash_password("resident123"),
            "role": Role.user,
            "is_active": True,
        },
        {
            "username": "staff1",
            "email": "staff1@smarthousing.com",
            "hashed_password": hash_password("staff123"),
            "role": Role.user,
            "is_active": True,
        },
    ]
    
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
    
    await session.commit()
    print(f"✓ Seeded {len(users_data)} users")


async def seed_cameras(session: AsyncSession):
    """Seed cameras table"""
    print("Seeding cameras...")
    
    # Check if cameras already exist
    result = await session.execute(text("SELECT COUNT(*) FROM cameras"))
    count = result.scalar()
    if count > 0:
        print(f"  Skipping - {count} cameras already exist")
        return
    
    cameras_data = [
        {
            "code": "CAM-001",
            "name": "Main Gate Entrance",
            "location": "Main Gate - Entry",
            "stream_url": "rtsp://camera1.local/stream",
            "type": CameraType.BOTH,
            "is_active": True,
        },
        {
            "code": "CAM-002",
            "name": "Main Gate Exit",
            "location": "Main Gate - Exit",
            "stream_url": "rtsp://camera2.local/stream",
            "type": CameraType.BOTH,
            "is_active": True,
        },
        {
            "code": "CAM-003",
            "name": "Parking Lot A",
            "location": "Parking Lot - Section A",
            "stream_url": "rtsp://camera3.local/stream",
            "type": CameraType.PLATE,
            "is_active": True,
        },
        {
            "code": "CAM-004",
            "name": "Lobby Entrance",
            "location": "Main Building Lobby",
            "stream_url": "rtsp://camera4.local/stream",
            "type": CameraType.FACE,
            "is_active": True,
        },
        {
            "code": "CAM-005",
            "name": "Rear Gate",
            "location": "Rear Service Gate",
            "stream_url": "rtsp://camera5.local/stream",
            "type": CameraType.BOTH,
            "is_active": False,  # Inactive camera
        },
    ]
    
    for camera_data in cameras_data:
        camera = Camera(**camera_data)
        session.add(camera)
    
    await session.commit()
    print(f"✓ Seeded {len(cameras_data)} cameras")


async def seed_persons(session: AsyncSession):
    """Seed persons table"""
    print("Seeding persons...")
    
    # Check if persons already exist
    result = await session.execute(text("SELECT COUNT(*) FROM persons"))
    count = result.scalar()
    if count > 0:
        print(f"  Skipping - {count} persons already exist")
        return
    
    # Get users for owner_id reference
    users_result = await session.execute(text("SELECT id, username FROM users ORDER BY username"))
    users = {row.username: row.id for row in users_result}
    
    persons_data = [
        {
            "name": "John Smith",
            "role": PersonRole.RESIDENT,
            "flat_no": "A-101",
            "phone": "+1234567890",
            "photo_url": "https://example.com/photos/john_smith.jpg",
            "is_active": True,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": None,
        },
        {
            "name": "Sarah Johnson",
            "role": PersonRole.RESIDENT,
            "flat_no": "A-102",
            "phone": "+1234567891",
            "photo_url": "https://example.com/photos/sarah_johnson.jpg",
            "is_active": True,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": None,
        },
        {
            "name": "Mike Wilson",
            "role": PersonRole.STAFF,
            "flat_no": "STAFF-001",
            "phone": "+1234567892",
            "photo_url": "https://example.com/photos/mike_wilson.jpg",
            "is_active": True,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": None,
        },
        {
            "name": "Emily Brown",
            "role": PersonRole.STAFF,
            "flat_no": "STAFF-002",
            "phone": "+1234567893",
            "photo_url": "https://example.com/photos/emily_brown.jpg",
            "is_active": True,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": None,
        },
        {
            "name": "Guest Visitor",
            "role": PersonRole.VISITOR,
            "flat_no": "VISITOR-001",
            "phone": "+1234567894",
            "photo_url": "https://example.com/photos/guest_visitor.jpg",
            "is_active": True,
            "valid_from": datetime.now(timezone.utc),
            "valid_until": datetime.now(timezone.utc) + timedelta(days=1),
        },
    ]
    
    for person_data in persons_data:
        person = Person(**person_data)
        session.add(person)
    
    await session.commit()
    print(f"✓ Seeded {len(persons_data)} persons")


async def seed_vehicles(session: AsyncSession):
    """Seed vehicles table"""
    print("Seeding vehicles...")
    
    # Check if vehicles already exist
    result = await session.execute(text("SELECT COUNT(*) FROM vehicles"))
    count = result.scalar()
    if count > 0:
        print(f"  Skipping - {count} vehicles already exist")
        return
    
    # Get users for owner_id reference
    users_result = await session.execute(text("SELECT id, username FROM users ORDER BY username"))
    users = {row.username: row.id for row in users_result}
    
    vehicles_data = [
        {
            "plate_number": "ABC-1234",
            "owner_id": users.get("resident1"),
            "owner_name": "Resident One",
            "flat_no": "A-101",
            "vehicle_type": "Sedan",
            "color": "Black",
            "status": VehicleStatus.RESIDENT,
            "notes": "Primary vehicle",
        },
        {
            "plate_number": "XYZ-5678",
            "owner_id": users.get("resident1"),
            "owner_name": "Resident One",
            "flat_no": "A-101",
            "vehicle_type": "SUV",
            "color": "White",
            "status": VehicleStatus.RESIDENT,
            "notes": "Secondary vehicle",
        },
        {
            "plate_number": "DEF-9012",
            "owner_id": users.get("staff1"),
            "owner_name": "Staff One",
            "flat_no": "STAFF-001",
            "vehicle_type": "Van",
            "color": "Blue",
            "status": VehicleStatus.STAFF,
            "notes": "Maintenance vehicle",
        },
        {
            "plate_number": "GHI-3456",
            "owner_id": None,
            "owner_name": "Delivery Service",
            "flat_no": "DELIVERY",
            "vehicle_type": "Truck",
            "color": "Red",
            "status": VehicleStatus.VISITOR,
            "notes": "Regular delivery",
        },
        {
            "plate_number": "BLK-7890",
            "owner_id": None,
            "owner_name": "Unknown",
            "flat_no": "N/A",
            "vehicle_type": "Motorcycle",
            "color": "Black",
            "status": VehicleStatus.BLACKLIST,
            "notes": "Trespassing vehicle",
        },
    ]
    
    for vehicle_data in vehicles_data:
        vehicle = Vehicle(**vehicle_data)
        session.add(vehicle)
    
    await session.commit()
    print(f"✓ Seeded {len(vehicles_data)} vehicles")


async def seed_all():
    """Seed all tables"""
    print("=" * 50)
    print("Starting database seeding...")
    print("=" * 50)
    
    # Load dependencies
    load_all_dependencies()
    
    session = await get_db_session()
    try:
        # Seed in order to respect foreign key constraints
        await seed_users(session)
        await seed_cameras(session)
        await seed_persons(session)
        await seed_vehicles(session)
        
        print("=" * 50)
        print("✓ Database seeding completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
        database = container.resolve('database')
        await database.disconnect()


async def clear_all():
    """Clear all seeded data (in reverse order of dependencies)"""
    print("=" * 50)
    print("Clearing seeded data...")
    print("=" * 50)
    
    # Load dependencies
    load_all_dependencies()
    
    session = await get_db_session()
    try:
        # Clear in reverse order to respect foreign key constraints
        await session.execute(text("DELETE FROM vehicles"))
        await session.execute(text("DELETE FROM persons"))
        await session.execute(text("DELETE FROM cameras"))
        await session.execute(text("DELETE FROM users"))
        
        await session.commit()
        
        print("=" * 50)
        print("✓ All seeded data cleared successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Error during clearing: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
        database = container.resolve('database')
        await database.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_all())
    else:
        asyncio.run(seed_all())
