import os
import shutil
import uuid
import re
from pathlib import Path

# Backup root directory for all operations
BACKUP_ROOT = Path(__file__).parent / "backups"
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

# Default limits
MAX_FILE_READ = 1024 * 1024  # 1 MB
MAX_SEARCH_RESULTS = 1000


def parse_args(args_str: str) -> dict:
    """
    Parse key="value" pairs from the args string.
    """
    # Support both triple-quoted (multi-line) and single-quoted parameters
    result = {}
    # Match triple-quoted values for multi-line content
    triple_pattern = re.compile(r"(\w+)\s*=\s*\"\"\"([\s\S]*?)\"\"\"")
    for m in triple_pattern.finditer(args_str):
        result[m.group(1)] = m.group(2)
    # Remove matched triple-quoted segments before single-line parse
    args_str = triple_pattern.sub('', args_str)
    # Match standard key="value"
    pattern = re.compile(r"(\w+)\s*=\s*\"([^\"]*)\"")
    for m in pattern.finditer(args_str):
        result[m.group(1)] = m.group(2)
    return result


def backup_path(src: Path) -> tuple:
    """
    Backup the given file or directory under BACKUP_ROOT with a new UUID.
    Returns the backup ID and backup path.
    """
    run_id = uuid.uuid4().hex
    base_dir = BACKUP_ROOT / run_id
    # Preserve the relative structure
    try:
        rel = src.relative_to(Path(__file__).parent)
    except Exception:
        rel = src.name
    dest = base_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if src.is_file():
        shutil.copy2(src, dest)
    elif src.is_dir():
        shutil.copytree(src, dest)
    return run_id, str(dest)


def execute(args: str) -> dict:
    """
    Main entry for the files tool. Supports: list, read, write, create, delete, search.
    """
    params = parse_args(args)

    # LIST directory
    if 'list' in params:
        path = Path(params['list'])
        if not path.is_dir():
            return {'success': False, 'error': f"{path} is not a directory"}
        entries = [p.name for p in path.iterdir()]
        return {'success': True, 'result': entries}

    # READ file
    if 'read' in params:
        path = Path(params['read'])
        if not path.is_file():
            return {'success': False, 'error': f"{path} is not a file"}
        # Read full text with size limit
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()
        # If specific line range requested
        if 'lines' in params:
            try:
                start_str, end_str = params['lines'].split('-')
                start, end = int(start_str), int(end_str)
                if start < 1 or end < start:
                    raise ValueError
            except Exception:
                return {'success': False, 'error': f"Invalid lines parameter: {params['lines']}"}
            selected = lines[start - 1:end]
            return {'success': True, 'result': '\n'.join(selected)}
        # Otherwise return entire file, truncated if needed
        text = '\n'.join(lines)
        if len(text) > MAX_FILE_READ:
            text = text[:MAX_FILE_READ]
        return {'success': True, 'result': text}

    # WRITE file with backup
    if 'write' in params and 'content' in params:
        path = Path(params['write'])
        backup_info = None
        if path.exists():
            run_id, dest = backup_path(path)
            backup_info = {'backup_id': run_id, 'backup_path': dest}
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(params['content'])
        result = {'message': f"Wrote to {path}"}
        if backup_info:
            result['backup'] = backup_info
        return {'success': True, 'result': result}

    # CREATE file or directory with backup
    if 'create' in params:
        path = Path(params['create'])
        typ = params.get('type', 'file')
        backup_info = None
        if path.exists():
            run_id, dest = backup_path(path)
            backup_info = {'backup_id': run_id, 'backup_path': dest}
        if typ == 'dir':
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        result = {'message': f"Created {typ} at {path}"}
        if backup_info:
            result['backup'] = backup_info
        return {'success': True, 'result': result}

    # DELETE file or directory with backup
    if 'delete' in params:
        path = Path(params['delete'])
        if not path.exists():
            return {'success': False, 'error': f"{path} does not exist"}
        run_id, dest = backup_path(path)
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        result = {'message': f"Deleted {path}", 'backup': {'backup_id': run_id, 'backup_path': dest}}
        return {'success': True, 'result': result}

    # SEARCH files and directories by regex
    if 'search' in params and 'pattern' in params:
        root = Path(params['search'])
        if not root.exists():
            return {'success': False, 'error': f"{root} does not exist"}
        pat = re.compile(params['pattern'])
        matches = []
        for p in root.rglob('*'):
            if pat.search(p.name):
                matches.append(str(p))
                if len(matches) >= MAX_SEARCH_RESULTS:
                    break
        return {'success': True, 'result': matches}

    return {'success': False, 'error': 'Invalid or missing parameters for files tool'}
