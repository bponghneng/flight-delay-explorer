"""Tests for data models."""

from flight_delay_explorer.models import DelayCategory, FlightRecord, QueryParams


class TestDelayCategory:
    """Test DelayCategory enum."""

    def test_delay_category_values(self):
        """Test that DelayCategory enum has correct string values."""
        assert DelayCategory.CANCELLED.value == "cancelled"
        assert DelayCategory.DIVERTED.value == "diverted"
        assert DelayCategory.ON_TIME.value == "on time"
        assert DelayCategory.MAJOR_DELAY.value == "major delay"
        assert DelayCategory.MINOR_DELAY.value == "minor delay"
        assert DelayCategory.SEVERE_DELAY.value == "severe delay"

    def test_delay_category_membership(self):
        """Test that all expected values are in DelayCategory."""
        expected_values = {
            "cancelled",
            "diverted",
            "on time",
            "major delay",
            "minor delay",
            "severe delay",
        }
        actual_values = {category.value for category in DelayCategory}
        assert actual_values == expected_values


class TestFlightRecord:
    """Test FlightRecord dataclass."""

    def test_flight_record_creation(self):
        """Test creating a FlightRecord with all required fields."""
        record = FlightRecord(
            arrival_delay=25,
            destination_icao="KLAX",
            flight_date="2024-01-01",
            flight_icao="AAL123",
            flight_status=DelayCategory.MINOR_DELAY,
            origin_icao="KJFK",
        )

        assert record.arrival_delay == 25
        assert record.destination_icao == "KLAX"
        assert record.flight_date == "2024-01-01"
        assert record.flight_icao == "AAL123"
        assert record.flight_status == DelayCategory.MINOR_DELAY
        assert record.origin_icao == "KJFK"

    def test_flight_record_type_annotations(self):
        """Test that FlightRecord has proper type annotations."""
        import inspect

        signature = inspect.signature(FlightRecord.__init__)
        params = signature.parameters

        # Skip 'self' parameter
        field_params = {name: param for name, param in params.items() if name != "self"}

        # Check that fields exist
        expected_fields = {
            "arrival_delay",
            "destination_icao",
            "flight_date",
            "flight_icao",
            "flight_status",
            "origin_icao",
        }
        assert set(field_params.keys()) == expected_fields

    def test_flight_record_with_cancelled_status(self):
        """Test FlightRecord with cancelled status."""
        record = FlightRecord(
            arrival_delay=0,
            destination_icao="KDEN",
            flight_date="2024-01-01",
            flight_icao="UAL456",
            flight_status=DelayCategory.CANCELLED,
            origin_icao="KORD",
        )

        assert record.flight_status == DelayCategory.CANCELLED
        assert record.arrival_delay == 0

    def test_flight_record_equality(self):
        """Test that FlightRecord instances can be compared for equality."""
        record1 = FlightRecord(
            arrival_delay=10,
            destination_icao="KATL",
            flight_date="2024-01-01",
            flight_icao="DAL789",
            flight_status=DelayCategory.ON_TIME,
            origin_icao="KMIA",
        )

        record2 = FlightRecord(
            arrival_delay=10,
            destination_icao="KATL",
            flight_date="2024-01-01",
            flight_icao="DAL789",
            flight_status=DelayCategory.ON_TIME,
            origin_icao="KMIA",
        )

        assert record1 == record2


class TestQueryParams:
    """Test QueryParams dataclass."""

    def test_query_params_creation(self):
        """Test creating QueryParams with required fields."""
        params = QueryParams(flight_date="2024-01-01")

        assert params.flight_date == "2024-01-01"

    def test_query_params_type_annotations(self):
        """Test that QueryParams has proper type annotations."""
        import inspect

        signature = inspect.signature(QueryParams.__init__)
        params = signature.parameters

        # Skip 'self' parameter
        field_params = {name: param for name, param in params.items() if name != "self"}

        # Check that flight_date field exists
        assert "flight_date" in field_params

    def test_query_params_equality(self):
        """Test that QueryParams instances can be compared for equality."""
        params1 = QueryParams(flight_date="2024-01-01")
        params2 = QueryParams(flight_date="2024-01-01")
        params3 = QueryParams(flight_date="2024-01-02")

        assert params1 == params2
        assert params1 != params3
