# ADR-001: Subsystem Boundaries

## Decision

TargetModel
    Owns simulated world truth.

RadarSensor
    Converts truth + TaskRequest into a simulated measurement.

DetectionManager
    Converts measurements into plots/detections.

TrackManager
    Maintains track state from plots.

Scheduler
    Decides what radar task happens next.
