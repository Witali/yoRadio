# Firmware artifacts

- Save every successful production firmware build intended for testing or
  hand-off under the repository''s `firmware/` directory. Do not leave the only
  copy in an ignored build directory.
- Save replaceable, unreleased builds under
  `firmware/development/<variant>/app.bin`.
- Save releases under `firmware/<version>/<variant>/` and never overwrite or
  remove an existing versioned release.

