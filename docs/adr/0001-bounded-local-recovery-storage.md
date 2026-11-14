---
status: accepted
date: 2026-11-14
---

# Bound local recovery confidentiality and coverage

MVP session history and covered workspace checkpoints use private, unencrypted local storage, with ignored files and configured sensitive paths excluded from checkpoints. We accept that unidentified user secrets can remain in covered files/history rather than making encrypted recovery and key recovery part of the MVP. Known Mocha credentials retain their separate protection requirements, and excluded-file mutation requires approval explaining absent rewind coverage.

Exclusion is a recovery rule: it does not prevent a read from entering model context or history. No automatic separate `.env` backup is allowed. Retain sessions and referenced recovery/evidence until explicit deletion with a preview. Exact path/restore rules are defined in the [storage contract](../contracts/storage-and-context.md).
