# Accessing CERN Open Data on lxplus

All CERN Open Data files live on EOS at `/eos/opendata/` and are publicly readable — no download or authentication needed.

## Option 1: Direct Filesystem (FUSE Mount)

EOS is auto-mounted on lxplus (not local server), so files are accessible as regular paths:

```bash
ls /eos/opendata/cms/
```

**Use when:** interactive exploration, quick checks, small-scale reads, scripting with standard tools (`cp`, `cat`, etc.).

**Avoid when:** batch jobs or heavy parallel I/O — FUSE can be flaky under load.

## Option 2: XRootD Protocol

Access files via the `eospublic.cern.ch` redirector using `root://` URLs:

```python
# ROOT
import ROOT
f = ROOT.TFile.Open("root://eospublic.cern.ch//eos/opendata/cms/<path>.root")

# uproot
import uproot
f = uproot.open("root://eospublic.cern.ch//eos/opendata/cms/<path>.root")
```

You can also copy files locally with `xrdcp`:

```bash
xrdcp root://eospublic.cern.ch//eos/opendata/cms/<path>.root ./local_copy.root
```

**Use when:** batch/grid jobs, remote access from outside CERN, streaming large files in analysis code, or any production workflow.

## Quick Reference

| Method | Prefix | Best for |
|---|---|---|
| FUSE | `/eos/opendata/...` | Interactive, browsing, small reads |
| XRootD | `root://eospublic.cern.ch//eos/opendata/...` | Batch jobs, remote access, production |
