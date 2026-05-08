import pytest
from app.simulation.engine import SimulationEngine
from app.schemas import SimulationRequest, TrainSchema, TrackSchema


class TestSimulationEngine:
    """Tests for the simulation engine calculations."""

    def test_single_segment_energy(self):
        request = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 500},
            tracks=[
                TrackSchema(length=500, bending=5, elevation=100)
            ]
        )
        engine = SimulationEngine()
        result = engine.simulate(request)
        assert result.total_energy > 0
        assert result.average_energy > 0
        assert len(result.points) == 1
        assert result.points[0].electricity_usage > 0

    def test_multiple_segments(self):
        request = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 12000},
            tracks=[
                TrackSchema(length=500, bending=5, elevation=100),
                TrackSchema(length=300, bending=10, elevation=50),
                TrackSchema(length=200, bending=0, elevation=0),
            ]
        )
        engine = SimulationEngine()
        result = engine.simulate(request)
        assert len(result.points) == 3
        assert pytest.approx(result.total_energy) == sum(p.electricity_usage for p in result.points)
        assert result.points[2].distance == 1000

    def test_elevation_impact(self):
        """Higher elevation should consume more energy."""
        engine = SimulationEngine()
        request1 = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 500},
            tracks=[TrackSchema(length=500, bending=0, elevation=100)]
        )
        request2 = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 500},
            tracks=[TrackSchema(length=500, bending=0, elevation=200)]
        )
        result1 = engine.simulate(request1)
        result2 = engine.simulate(request2)
        assert result2.total_energy > result1.total_energy

    def test_weight_impact(self):
        """Heavier trains should consume more energy."""
        engine = SimulationEngine()
        request1 = SimulationRequest(
            train=TrainSchema(weight=1000, train_cars=6),
            line={"total_length": 500},
            tracks=[TrackSchema(length=500, bending=0, elevation=100)]
        )
        request2 = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 500},
            tracks=[TrackSchema(length=500, bending=0, elevation=100)]
        )
        result1 = engine.simulate(request1)
        result2 = engine.simulate(request2)
        assert result2.total_energy > result1.total_energy

    def test_custom_calibration_factors(self):
        """Custom factors should affect energy calculation."""
        request = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 1000},
            tracks=[TrackSchema(length=1000, bending=10, elevation=100)]
        )
        engine1 = SimulationEngine(elevation_factor=0.1, curve_factor=0.05, distance_factor=0.8)
        engine2 = SimulationEngine(elevation_factor=0.2, curve_factor=0.05, distance_factor=0.8)
        result1 = engine1.simulate(request)
        result2 = engine2.simulate(request)
        assert result2.total_energy > result1.total_energy

    def test_calculation_formula_components(self):
        """Verify individual formula components are summed correctly."""
        request = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 1000},
            tracks=[TrackSchema(length=1000, bending=10, elevation=100)]
        )
        engine = SimulationEngine(elevation_factor=0.1, curve_factor=0.05, distance_factor=0.8)
        # elevation: 100 * 2000 * 0.1 = 20,000
        # curve: 10 * 0.05 = 0.5
        # distance: 1000 * 0.8 / 1000 = 0.8
        # total = 20,001.3
        result = engine.simulate(request)
        assert result.points[0].electricity_usage == 20001.30

    def test_long_track(self):
        """Very long track should handle large values."""
        request = SimulationRequest(
            train=TrainSchema(weight=5000, train_cars=20),
            line={"total_length": 50000},
            tracks=[TrackSchema(length=50000, bending=30, elevation=500)]
        )
        engine = SimulationEngine()
        result = engine.simulate(request)
        assert result.total_energy > 0
        assert result.points[0].distance == 50000

    def test_zero_bending_no_elevation(self):
        """Flat, straight track still consumes energy (distance component)."""
        request = SimulationRequest(
            train=TrainSchema(weight=2000, train_cars=12),
            line={"total_length": 1000},
            tracks=[TrackSchema(length=1000, bending=0, elevation=0)]
        )
        engine = SimulationEngine()
        result = engine.simulate(request)
        assert result.total_energy > 0
        point = result.points[0]
        assert point.electricity_usage == round(1000 * 0.8 / 1000, 2)  # distance component only


class TestSchemaValidation:
    """Tests for request/response schema validation."""

    def test_valid_request_passes(self):
        data = {
            "train": {"weight": 2000, "train_cars": 12},
            "line": {"total_length": 12000},
            "tracks": [{"length": 500, "bending": 5, "elevation": 100}]
        }
        request = SimulationRequest(**data)
        assert request.train.weight == 2000
        assert len(request.tracks) == 1

    def test_invalid_weight_raises(self):
        with pytest.raises(Exception):
            SimulationRequest(
                train=TrainSchema(weight=-100, train_cars=10),
                line={"total_length": 1000},
                tracks=[TrackSchema(length=100, bending=0, elevation=0)]
            )

    def test_invalid_bending_raises(self):
        with pytest.raises(Exception):
            SimulationRequest(
                train=TrainSchema(weight=2000, train_cars=10),
                line={"total_length": 1000},
                tracks=[TrackSchema(length=100, bending=100, elevation=0)]
            )
