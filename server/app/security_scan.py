# server/app/security_scan.py
"""Simple upload-time security scanner for plugin packages.

Features:
- Safely extract tarball to temp dir (prevents path traversal)
- Static checks:
  - presence of native binaries (.so/.dll/.dylib) => HIGH
  - presence of wheel files or compiled extensions => HIGH
  - large files (>100MB) => MEDIUM/HIGH
  - suspicious Python builtins/use (exec/eval, os.system, subprocess, socket, ctypes, cffi) => MEDIUM/HIGH
  - excessive number of files (>5000) => MEDIUM
  - presence of .git, node_modules => INFO/WARNING
  - manifest.json presence and basic validation
- Produces JSON report with severity levels and returns (ok:bool, report:dict)

Note: This is a static analyzer only. For stronger assurance, run dynamic analysis in an isolated container.
"""
import tarfile
import tempfile
from pathlib import Path
import shutil
import os
import json
import re
import ast

MAX_FILES = 5000
LARGE_FILE_BYTES = 100 * 1024 * 1024  # 100 MB
SUSPICIOUS_PATTERNS = [
    r"\beval\b",
    r"\bexec\b",
    r"os\.system\(" ,
    r"subprocess\.",
    r"socket\.",
    r"requests\.",
    r"urllib\.",
    r"ctypes\.",
    r"cffi\.",
    r"dlopen\(",
    r"open\(.+\b/w",  # attempts to write maybe (heuristic)
]

NATIVE_EXT = ['.so', '.dll', '.dylib', '.pyd']

def _safe_extract_tar(tar_path: Path, dest: Path):
    """Extract tar safely (prevent path traversal)."""
    with tarfile.open(tar_path, 'r:*') as tf:
        for member in tf.getmembers():
            member_path = dest.joinpath(member.name)
            if not str(member_path.resolve()).startswith(str(dest.resolve())):
                raise RuntimeError(f"Potential path traversal in tar file: {member.name}")
        tf.extractall(dest)

def _is_text_file(path: Path) -> bool:
    try:
        with open(path, 'rb') as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return False
            return True
    except Exception:
        return False

def _scan_python_file(path: Path):
    findings = []
    try:
        src = path.read_text(encoding='utf-8', errors='ignore')
        # AST-based import scanning
        try:
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        if name.startswith(('os','subprocess','socket','ctypes','cffi','urllib','requests')):
                            findings.append(('import', name))
                elif isinstance(node, ast.Call):
                    # function calls - detect eval/exec via name
                    func = node.func
                    if isinstance(func, ast.Name) and func.id in ('eval','exec','compile'):
                        findings.append(('call', func.id))
                    elif isinstance(func, ast.Attribute):
                        val = getattr(func, 'attr', '')
                        if val in ('system','popen'):
                            findings.append(('call', val))
        except Exception:
            # fallback to regex heuristics
            for pat in SUSPICIOUS_PATTERNS:
                if re.search(pat, src):
                    findings.append(('pattern', pat))
    except Exception:
        findings.append(('error', 'cannot read file'))
    return findings

def scan_package(tar_bytes: bytes):
    """Scan an uploaded tarball bytes. Returns (ok:bool, report:dict)."""
    tmpdir = Path(tempfile.mkdtemp(prefix='cs_scan_'))
    report = {
        'files_scanned': 0,
        'issues': [],
        'summary': {'high':0, 'medium':0, 'low':0, 'info':0}
    }
    tar_path = tmpdir / 'upload.tar.gz'
    tar_path.write_bytes(tar_bytes)
    try:
        _safe_extract_tar(tar_path, tmpdir / 'pkg')
    except Exception as e:
        report['issues'].append({'severity':'high','msg':f'extraction_failed: {e}'})
        report['error'] = str(e)
        shutil.rmtree(tmpdir, ignore_errors=True)
        return False, report

    pkgdir = tmpdir / 'pkg'
    all_files = list(pkgdir.rglob('*'))
    report['files_scanned'] = len(all_files)
    if len(all_files) > MAX_FILES:
        report['issues'].append({'severity':'medium','msg':'too_many_files','count': len(all_files)})
        report['summary']['medium'] += 1

    for p in all_files:
        try:
            if p.is_dir():
                # skip
                continue
            rel = p.relative_to(pkgdir)
            size = p.stat().st_size
            # large files
            if size >= LARGE_FILE_BYTES:
                report['issues'].append({'severity':'high','msg':'large_file','path':str(rel),'size':size})
                report['summary']['high'] += 1
            # native binaries
            if p.suffix.lower() in NATIVE_EXT:
                report['issues'].append({'severity':'high','msg':'native_binary_found','path':str(rel)})
                report['summary']['high'] += 1
            # wheel or egg
            if p.suffix.lower() in ('.whl', '.egg'):
                report['issues'].append({'severity':'high','msg':'compiled_package_found','path':str(rel)})
                report['summary']['high'] += 1
            # python files scan
            if p.suffix.lower() in ('.py', '.pyw'):
                findings = _scan_python_file(p)
                if findings:
                    report['issues'].append({'severity':'medium','msg':'suspicious_python','path':str(rel),'findings': findings})
                    report['summary']['medium'] += 1
            # archive inside
            if p.suffix.lower() in ('.zip', '.tar', '.gz', '.tgz'):
                report['issues'].append({'severity':'info','msg':'nested_archive','path':str(rel)})
                report['summary']['info'] += 1
            # node_modules or .git
            if '.git' in str(rel).split(os.sep):
                report['issues'].append({'severity':'info','msg':'contains_git_metadata','path':str(rel)})
                report['summary']['info'] += 1
            if 'node_modules' in str(rel).split(os.sep):
                report['issues'].append({'severity':'medium','msg':'contains_node_modules','path':str(rel)})
                report['summary']['medium'] += 1
        except Exception as e:
            report['issues'].append({'severity':'low','msg':'file_scan_error','path':str(p), 'error': str(e)})
            report['summary']['low'] += 1

    # manifest.json presence check
    manifest_candidates = list(pkgdir.rglob('manifest.json')) + list(pkgdir.rglob('plugin.json'))
    if not manifest_candidates:
        report['issues'].append({'severity':'high','msg':'manifest_missing'})
        report['summary']['high'] += 1
    else:
        # basic validation of first manifest
        try:
            mf = json.loads(manifest_candidates[0].read_text(encoding='utf-8'))
            if 'name' not in mf or 'version' not in mf:
                report['issues'].append({'severity':'high','msg':'manifest_invalid','path':str(manifest_candidates[0].relative_to(pkgdir))})
                report['summary']['high'] += 1
        except Exception as e:
            report['issues'].append({'severity':'high','msg':'manifest_read_error','error':str(e)})
            report['summary']['high'] += 1

    # Heuristic decision: fail if any high severity issues
    ok = report['summary']['high'] == 0
    # cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)
    return ok, report
