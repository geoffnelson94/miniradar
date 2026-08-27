# Interface Control Document (ICD) Guidelines

## Versioning
Breaking changes shall increment the
major interface version.

Backward-compatible additions shall increment the
minor version.

## Requirements

Every interface must define:

### 1. Interface Identification
    - Version
### 2. Purpose
    - Why does it exist?
### 3. Participating Subsystems
    - Producer
    - Consumer
## 4. Interface Data
    - Messages
## 5. Timing
    - max latency
    - max throughput
    - nominal throughput
    - Timestamp semantics
## 6. Coordinate System
    - relavant coordinate frames
## 7. Units
## 8. Message Ordering
    - Rules for producer
    - Rules for consumer
## 9. Reliability
    - Rules for producer
    - Rules for consumer
## 10. Invalid Data
    - Rejection criteria
    - Failure behavior
## 11. Ownership
    - Creation
    - Mutability
## 12. Transport
    - communication layer
## 13. Initialization
    - Ready state
    - policies
## 14. Shutdown
    - policies
## 15. Verification
    - Test requirements