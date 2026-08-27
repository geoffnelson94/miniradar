# Architectural guidelines

## Subsystem ownership
Each subsystem owns its internal state.

Other subsystems interact through defined interfaces
rather than accessing internal implementation objects.

## Dependency direction
Higher-level control may depend on lower-level services.

Lower-level services shall not depend directly on higher-level
mission behavior.

## Seperation of concerns
1. The logical interface between subsystems shall not depend on the transport mechanism.
2. subsystems interact through defined interfaces
rather than accessing internal implementation objects