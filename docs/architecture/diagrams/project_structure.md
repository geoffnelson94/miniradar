mini_radar/
│
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── requirements/
│   │
│   ├── system/
│   │   ├── SYS-REQ-001.md
│   │   ├── SYS-REQ-002.md
│   │   └── SYS-REQ-003.md
│   │
│   ├── mission/
│   │   └── MIS-REQ-001.md
│   │
│   ├── detection/
│   │   └── DET-REQ-001.md
│   │
│   ├── tracking/
│   │   ├── TRK-REQ-001.md
│   │   ├── TRK-REQ-002.md
│   │   └── TRK-REQ-003.md
│   │
│   └── scheduling/
│       └── SCH-REQ-001.md
│
├── architecture/
│   │
│   ├── system_architecture.md
│   ├── logical_architecture.md
│   ├── physical_architecture.md
│   ├── data_flow.md
│   ├── control_flow.md
│   ├── timing_architecture.md
│   ├── deployment_view.md
│   │
│   ├── decisions/
│   │   ├── ADR-001-subsystem-boundaries.md
│   │   ├── ADR-002-message-ownership.md
│   │   ├── ADR-003-communication-model.md
│   │   └── ADR-004-time-model.md
│   │
│   └── diagrams/
│       ├── system_context.md
│       ├── subsystem_interactions.md
│       └── closed_loop.md
│
├── interfaces/
│   │
│   ├── README.md
│   │
│   ├── ICD-001-sensor-detection.md
│   ├── ICD-002-detection-tracking.md
│   ├── ICD-003-tracking-scheduler.md
│   └── ICD-004-scheduler-sensor.md
│   │
│   ├── schemas/
│   │   ├── detection_message.md
│   │   ├── track_message.md
│   │   ├── task_request.md
│   │   └── sensor_command.md
│   │
│   └── data_dictionary.md
│
├── config/
│   ├── default.yaml
│   ├── search.yaml
│   ├── track.yaml
│   └── radar.yaml
│
├── src/
│   │
│   ├── mission/
│   │   ├── __init__.py
│   │   ├── mission.py
│   │   ├── mission_manager.py
│   │   ├── radar_mode.py
│   │   └── constraints.py
│   │
│   ├── radar_management/
│   │   ├── __init__.py
│   │   ├── radar_controller.py
│   │   ├── mode_manager.py
│   │   ├── resource_manager.py
│   │   ├── scheduler.py
│   │   └── command_queue.py
│   │
│   ├── radar_control/
│   │   ├── __init__.py
│   │   ├── radar_command.py
│   │   ├── waveform_manager.py
│   │   ├── beam_manager.py
│   │   ├── timing_manager.py
│   │   └── calibration_manager.py
│   │
│   ├── hardware/
│   │   ├── __init__.py
│   │   │
│   │   ├── interfaces/
│   │   │   ├── radar_hardware.py
│   │   │   ├── fpga_interface.py
│   │   │   └── rf_interface.py
│   │   │
│   │   ├── simulated/
│   │   │   └── simulated_radar.py
│   │   │
│   │   └── rfsoc/
│   │       ├── rfsoc_driver.py
│   │       ├── axi_interface.py
│   │       └── dma_interface.py
│   │
│   ├── signal_processing/
│   │   ├── __init__.py
│   │   ├── waveform.py
│   │   ├── matched_filter.py
│   │   ├── range_fft.py
│   │   ├── doppler_fft.py
│   │   ├── beamforming.py
│   │   └── cfar.py
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── detection.py
│   │   ├── detection_manager.py
│   │   ├── plot.py
│   │   ├── plot_generator.py
│   │   └── detection_quality.py
│   │
│   ├── tracking/
│   │   ├── __init__.py
│   │   ├── track.py
│   │   ├── track_manager.py
│   │   ├── track_initiation.py
│   │   ├── track_confirmation.py
│   │   ├── track_deletion.py
│   │   ├── gating.py
│   │   ├── association.py
│   │   ├── kalman_filter.py
│   │   └── track_quality.py
│   │
│   ├── simulation/
│   │   ├── __init__.py
│   │   ├── scenario.py
│   │   ├── target.py
│   │   ├── target_dynamics.py
│   │   ├── environment.py
│   │   ├── clutter.py
│   │   ├── noise.py
│   │   ├── radar_model.py
│   │   └── truth.py
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── geometry.py
│   │   ├── units.py
│   │   ├── time.py
│   │   ├── configuration.py
│   │   └── logging.py
│   │
│   └── interfaces/
│       ├── __init__.py
│       ├── messages/
│       │   ├── detection_message.py
│       │   ├── track_message.py
│       │   ├── task_request.py
│       │   └── sensor_command.py
│       │
│       └── transport/
│           ├── interface.py
│           └── in_process.py
│
├── tests/
│   │
│   ├── unit/
│   │   ├── detection/
│   │   ├── tracking/
│   │   ├── scheduling/
│   │   └── common/
│   │
│   ├── integration/
│   │   ├── test_detection_to_track.py
│   │   ├── test_track_to_scheduler.py
│   │   └── test_radar_control_loop.py
│   │
│   ├── interface/
│   │   ├── test_detection_message.py
│   │   ├── test_track_message.py
│   │   └── test_task_request.py
│   │
│   └── scenarios/
│       ├── test_single_target.py
│       ├── test_multiple_targets.py
│       ├── test_crossing_targets.py
│       ├── test_missed_detections.py
│       └── test_clutter.py
│
├── notebooks/
│   ├── 01_target_motion.ipynb
│   ├── 02_measurement_noise.ipynb
│   ├── 03_detection.ipynb
│   ├── 04_kalman_filter.ipynb
│   ├── 05_data_association.ipynb
│   ├── 06_track_management.ipynb
│   ├── 07_radar_scheduling.ipynb
│   └── 08_closed_loop_radar.ipynb
│
└── docs/
    ├── getting_started.md
    ├── architecture_guide.md
    ├── interface_guide.md
    └── design_notes.md