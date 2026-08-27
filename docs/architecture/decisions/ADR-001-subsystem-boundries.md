# ADR-001: Subsystem Boundaries

## Decision

The radar software shall separate Detection and Tracking
into independent logical subsystems.

Detection is responsible for identifying candidate radar
observations and producing standardized Plot data.

Tracking is responsible for maintaining persistent estimates of objects using Plot data.

Tracking shall not depend on the internal implementation of the Detection subsystem.

The interface between the two subsystems shall be defined using a standardized message contract.