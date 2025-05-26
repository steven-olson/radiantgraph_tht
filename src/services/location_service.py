from sqlalchemy.orm import Session
from src.data.tables.location import Location, LocationType
from src.rest_api.schemas import LocationCreate


class LocationService:

    def __init__(self, db: Session):
        self.db = db

    def create_location(self, request: LocationCreate) -> Location:
        location = Location(
            location_type=request.location_type,
            address_line_1=request.address_line_1,
            address_line_2=request.address_line_2 or "",
            city=request.city,
            state=request.state,
            zip_code=request.zip_code
        )
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location)
        return location
