# Build Artifact Policy

This directory contains generated PK3 overlay artifacts.

Do not treat any PK3 in this directory as editable source data.

The development launch order will be:

1. `doda-core`
2. A generated content overlay from this folder

The content workbench must build new artifacts rather than overwriting source
archives in place.
