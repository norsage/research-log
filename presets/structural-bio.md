# Structural bioinformatics libraries

Last checked: 2026-09. Say so when you offer it if that date is old.

Reference for choosing dependencies. Write into the project the packages they
chose, with versions, in the tools table, plus a protocol for any tool whose
installation has traps.

The environment itself is in `python-uv.md` or `conda.md`. Those two can also
be combined: a uv project keeps one package that will not co-solve, or is
large and separately licensed, in its own conda environment. PyRosetta is the
usual one. `conda.md` has the rules for that split.

## Task to library

| Task | Reach for | Notes |
|---|---|---|
| read and write PDB/mmCIF | gemmi | C++ core with Python bindings, fastest at PDB-wide scale, also does maps, symmetry and neighbour search |
| vectorised analysis over structures | biotite | structures are numpy ndarrays, so downstream numpy work needs no conversion |
| solvent-accessible surface | freesasa | |
| protonation and electrostatics | pdb2pqr, then apbs | binaries, conda-forge |
| repairing a structure before simulation | pdbfixer | missing atoms, missing loops, hydrogens, water box |
| molecular dynamics | openmm | Python-native, GPU. gromacs is faster for long production runs and is a large external dependency |
| trajectories | MDAnalysis | |
| fetching from the PDB | rcsb-api | |
| graphs over structures | torch-geometric with torch-cluster | |
| mutating, repacking, per-residue energy terms | PyRosetta | licensed, versioned by year and week, usually its own conda environment |
| ddG and interface energies from an empirical function | FoldX | licensed binary, `BuildModel`, `AnalyseComplex`, `RepairPDB` |

biopython is the one everyone else's code imports. It parses slower than gemmi
or biotite, so reach for it when reading someone else's pipeline; default to
gemmi.

## Traps worth naming before they hit

- **pdbfixer's version tracks openmm's.** Install the pair in one conda solve
  from conda-forge instead of adding one to an environment that already has
  the other.
- **MDAnalysis tutorials written before the namespace change** import
  `simtk.openmm.app`. Current code uses `openmm.app`.
- **torch-geometric's kNN backend moved to pyg-lib**, which has no macOS-arm
  wheel. A project that trained through torch-cluster needs that pin kept,
  and the pin belongs in the manifest with the reason beside it.
- **gromacs** is a system binary, not a Python package. It goes in the tools
  table with its version, and its build options go in a protocol.
- **PyRosetta usually ships for a Python version behind the project's**, which
  makes importing it impossible and a subprocess the only route. Put the
  isolated half in its own directory with a driver that names it, and call
  `pyrosetta.init()` once per batch of jobs. Per structure, PyRosetta dominates
  the runtime.
- **FoldX is a licensed binary with no Python API.** Every call is a
  subprocess in a working directory it writes into, so runs need separate
  directories to stay parallelisable.

## What not to claim

Published parser benchmarks are old and most were written by the author of one
of the parsers. If the choice actually matters for their data volume, say the
comparison is unsettled and offer to time both on their own files.
