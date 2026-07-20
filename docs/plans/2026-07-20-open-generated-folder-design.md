# Open Generated Folder Design

## Goal

Display the selected generation folder in Caption automatically after a batch
finishes successfully.

## Behavior

`CaptionApp._finish_generation` will retain the existing status and control
reset, then call `open_folder` with `generation_folder`. This applies whether
the run generated missing captions or skipped every image during a resumed run.

The existing `open_folder` method flushes an unsaved caption before switching,
loads the folder's image list, rebuilds thumbnails, and displays its first
image. Generation errors continue through `_fail_generation` and do not switch
the editor's folder.

## Testing

Extend the non-GUI `CaptionApp` tests with a minimally constructed app whose UI
methods are replaced by recording functions. The regression test calls
`_finish_generation`, asserts that the controls and completion status update,
and verifies that the generation folder is opened exactly once. The existing
startup test continues to prove that launching Caption does not open a dialog.
