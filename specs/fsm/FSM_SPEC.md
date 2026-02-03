GEMIVAS FSM SPEC

STATES:
scouted
downloaded
probed
analyzed
ranked
published
dropped
quarantine

TRANSITIONS:
scouted->downloaded
downloaded->probed
probed->analyzed
analyzed->ranked
ranked->published
ranked->dropped
analyzed->quarantine

ERROR STATES:
stuck
retry_exceeded

TASK TYPES:
Scout
Download
Probe
Analyze
Rank
Transcode
Selfheal
