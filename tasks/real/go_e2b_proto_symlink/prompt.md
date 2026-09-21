The filesystem protocol needs to represent symbolic links as a distinct file type.

Add `FILE_TYPE_SYMLINK` with numeric value `3` to the filesystem `FileType` definition and ensure the generated Go binding exposes the corresponding `FileType_FILE_TYPE_SYMLINK` value. Keep the repository's generated bindings consistent with their canonical source.
