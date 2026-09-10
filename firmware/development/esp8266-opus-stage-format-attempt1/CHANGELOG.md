# Rejected stage-profile serialization, 2026-09-10

The decoder benchmark completed (state3/error0), but the stage profile is
INVALID: SDK nano printf emitted `lu` for unsupported `%llu`, also consuming
the following arguments incorrectly. Do not interpret subsequent stage fields.
The raw invalid response and observer errors are retained. The host observer
was stopped after confirming the completed state from the raw response;
there was no second benchmark start and no USB reset.

Replaced with two32-bit cycle words. This image is retained only as evidence,
not recommended for flashing. The ten prior stage0/control runs are separate
from this failed attempt; the fixed pair will be measured again.
