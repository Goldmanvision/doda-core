# Deadzone Data Flow

Status: Source-confirmed

The DoDA deadzone system data flow is strictly partitioned:

1. **Input Capture**: `DoDA/Aim/AimInput.zs` (EventHandler) captures raw mouse input and dispatches it to CVars (`doda_raw_mouse_x`, `doda_raw_mouse_y`).
2. **State & Math**: `DoDA/CharacterClasses/FieldAgent.zs` is the sole authority. It consumes the raw mouse CVars in `Tick()`, applies smoothing, calculates angular offsets (yaw/pitch), and enforces limits (`DeadzoneYawLimit`, `DeadzonePitchLimit`).
3. **Presentation**: `DoDA/UI/FieldAgent/HUDDeadzone.zs` and `DoDA/UI/FieldAgent/HUDDeadzoneBridge.zs` consume the state from `FieldAgent` for rendering only. They do not own or mutate deadzone state.

All weapon modules consume the established deadzone state from the player instance for trace/firing logic.
