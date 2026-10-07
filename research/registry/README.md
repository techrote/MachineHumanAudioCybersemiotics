# Live research registry

The canonical live state is explicitly **not_started**. There are no live source,
study, extraction or claim records. Synthetic examples are kept in
[tests/fixtures/records/v1](../../tests/fixtures/records/v1/README.md).

The manifest declares canonical record roots, selected current claims and
requirements, stage declarations, bibliography and manuscript sidecars.
Each canonical record file is named ID.json and follows the
[executable v1 contract](../../schemas/README.md). Add lane roots to the manifest
before writing records in those lanes. Roots must stay in the allowed research
areas; overlapping roots, symlinks, path traversal and unregistered record files
are rejected. Only one file may own a logical ID.

Generated views are rebuilt from validated canonical records. They are never
edited independently and never ingest fixture data. The normal validation command
compares their exact bytes; the explicit rebuild option writes the four views.
See [validation commands](../../docs/VALIDATION.md).

The bibliography maps unique citation keys to exact source revisions. Empty
bibliographies are valid while the work has not begun. Manuscript bindings
identify the document hash, exact line ranges, bibliography keys and claim/source
revisions; they cannot make an unsupported claim scientifically valid.

Historical records are retained. Append revisions and amendments when evidence
changes. A check against a prior accepted snapshot or Git commit detects deletion
and rewriting; validating a standalone snapshot alone cannot establish its past.
