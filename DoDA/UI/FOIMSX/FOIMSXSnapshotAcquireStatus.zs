/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXSnapshotAcquireStatus.zs
//
// FOIMS-X Standardized Snapshot Acquisition Status.
//
// Standardized outcome enumeration for FOIMS-X snapshot adapters representing
// success, unavailable source data, incompatible API version, and validation rejection.
//
// Scope & Boundary:
//   - Pure status enumeration: does not know Personnel or Assignment models, records, or fields.
//   - Zero native calls: does not call DoDA native queries.
//   - Zero lifecycle, input, tick, timer, or rendering operations.
*///////////////////////////|

enum EDoDAFOIMSXSnapshotAcquireStatus
{
    FOIMSX_ACQUIRE_UNAVAILABLE,
    FOIMSX_ACQUIRE_SUCCESS,
    FOIMSX_ACQUIRE_INCOMPATIBLE_VERSION,
    FOIMSX_ACQUIRE_REJECTED
};
