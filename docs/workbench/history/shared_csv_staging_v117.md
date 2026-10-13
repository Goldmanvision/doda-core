# Unique shared CSV staging v117

Shared write_rows uses a unique temporary file in the destination directory.
Staging is closed before replacement for Windows compatibility.
Failed row generation or replacement leaves the original destination intact.
The temporary file is removed after success or ordinary failure.
An unrelated legacy .csv.tmp file is not overwritten or deleted.
Column projection, blank missing values, UTF-8 and CRLF output are preserved.
v116 source-hash save checkpoints remain unchanged.
No interprocess locking or additional concurrency guarantee is introduced.
Seven regression tests use temporary files.
Expected tests: 676 baseline; 683 after installation.
No source CSVs, runtime behavior, export schemas or controls are changed.
