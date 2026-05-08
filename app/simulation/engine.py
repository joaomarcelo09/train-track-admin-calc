from typing import Optional
from app.schemas import SimulationRequest, SimulationResponse, SimulationPoint, TrainSchema, TrackSchema


class SimulationEngine:
    """
    Energy simulation engine for train route traversal.
    Calculates electricity consumption per track segment using configurable factors.
    """

    # Default calibration factors (modular for future improvements)
    ELEVATION_FACTOR = 0.1  # kWh per ton-meter of elevation
    CURVE_FACTOR = 0.05  # kWh per degree of bending (or per meter for radius)
    DISTANCE_FACTOR = 0.8  # kWh per kilometer track length

    def __init__(
        self,
        elevation_factor: Optional[float] = None,
        curve_factor: Optional[float] = None,
        distance_factor: Optional[float] = None,
    ):
        self.elevation_factor = (
            elevation_factor if elevation_factor is not None else self.ELEVATION_FACTOR
        )
        self.curve_factor = (
            curve_factor if curve_factor is not None else self.CURVE_FACTOR
        )
        self.distance_factor = (
            distance_factor if distance_factor is not None else self.DISTANCE_FACTOR
        )

    def simulate(self, request: SimulationRequest) -> SimulationResponse:
        """Simulate energy consumption across track segments."""
        points = []
        cumulative_distance = 0.0

        for i, track in enumerate(request.tracks):
            energy = self._calculate_segment_energy(request.train, track)
            cumulative_distance += track.length

            points.append(
                SimulationPoint(
                    track_index=i,
                    distance=cumulative_distance,
                    electricity_usage=energy,
                    track=track,
                )
            )

        total_energy = sum(p.electricity_usage for p in points)

        return SimulationResponse(
            total_energy=round(total_energy, 2),
            average_energy=round(total_energy / cumulative_distance, 4) if cumulative_distance > 0 else 0,
            points=points,
        )

    def _calculate_segment_energy(
        self,
        train: TrainSchema,
        track: TrackSchema,
    ) -> float:
        """Calculate energy consumption for a single segment."""
        weight_factor = train.weight
        elevation_component = track.elevation * weight_factor * self.elevation_factor
        curve_component = track.bending * self.curve_factor
        distance_component = track.length * self.distance_factor / 1000  # per km
        total_energy = elevation_component + curve_component + distance_component
        return round(total_energy, 2)
