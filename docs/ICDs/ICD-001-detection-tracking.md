# ICD-001: Detection-to-Tracking Interface

## 1. Interface Identification

Interface ID:
    ICD-001

Interface Name:
    Detection-to-Tracking

Version:
    1.0

Status:
    Draft


## 2. Purpose

This interface transfers validated radar plot information
from the Detection subsystem to the Tracking subsystem.


## 3. Participating Subsystems

Producer:
    Detection

Consumer:
    Tracking

## 5. Interface Data

Primary message:
    PlotMessage


## 7. Timing

Maximum producer-to-consumer latency:
    10 ms

Nominal throughput:
    10 plots/sec

Maximum throughput:
    100 plots/sec

Timestamp:
    Timestamp represents the time at which the radar
    measurement was acquired.

The consumer shall not substitute processing time
for measurement time.


## 8. Coordinate System

Position measurements shall be expressed in the
radar body coordinate frame.

X:
    Forward

Y:
    Left

Z:
    Up


## 9. Units

Range:
    meters

Range rate:
    meters/second

Azimuth:
    radians

Elevation:
    radians

Timestamp:
    seconds


## 10. Message Ordering

Messages shall contain a monotonically increasing
sequence number.

The consumer shall tolerate out-of-order messages.

Messages with timestamps older than the configured
maximum measurement age may be rejected.


## 11. Reliability

Individual plot messages may be lost.

Loss of a plot shall not terminate the Tracking subsystem.


## 12. Invalid Data

The Tracking subsystem shall reject plots containing:

- invalid timestamps
- NaN measurement values
- values outside configured physical limits


## 13. Ownership

The Detection subsystem owns creation of PlotMessage objects.

The Tracking subsystem shall treat received PlotMessage
objects as immutable.


## 14. Transport

Version 1:
    In-process function call.

Future implementations may use:
    - queue
    - shared memory
    - IPC
    - middleware


## 15. Initialization

The interface becomes active after both Detection and
Tracking subsystems report READY.


## 16. Shutdown

Detection shall stop producing new messages after
shutdown has been initiated.

Tracking shall process or discard remaining messages
according to shutdown policy.

## 18. Verification

The following shall be verified:

- valid messages are accepted
- invalid messages are rejected
- timestamps are preserved
- units are interpreted correctly
- dropped messages do not crash tracking
- out-of-order messages are handled correctly
- maximum message rate is supported
- latency requirement is satisfied