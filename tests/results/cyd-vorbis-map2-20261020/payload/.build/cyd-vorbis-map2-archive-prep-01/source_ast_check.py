"""Parse proposal sources only. Does not import/run pack.py or verify.py."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTR = b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n'
facts = {}
for name in ('pack.py', 'verify.py'):
    raw = (HERE / name).read_bytes()
    tree = ast.parse(raw, filename=name)
    imported = sorted({alias.name for node in tree.body if isinstance(node, ast.Import) for alias in node.names} |
                      {node.module for node in tree.body if isinstance(node, ast.ImportFrom)})
    assert not ({'subprocess', 'socket', 'urllib', 'requests', 'os'} & set(imported))
    assert any(isinstance(node, ast.Constant) and node.value == ATTR for node in ast.walk(tree))
    facts[name] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), parsed=True, imports=imported)
    if name == 'verify.py':
        profile = next(node.value.value for node in tree.body if isinstance(node, ast.Assign) and
                       any(isinstance(target, ast.Name) and target.id == 'FORBIDDEN_PROFILE' for target in node.targets))
        assert profile == r'^#define (LIMIT_TO_64kHz|CONFIG_FREERTOS_UNICORE)\b'
        assert profile[-2:] == '\\b' and '\x08' not in profile
        facts[name]['forbidden_profile_pattern'] = profile
plan = json.loads((HERE / 'plan.template.json').read_bytes())
assert len(plan['campaigns']) == 8 and len(plan['numeric']) == 3 and len(plan['hosts']) == 2
print(json.dumps(dict(status='SOURCE_AST_ONLY', files=facts,
    pending_roles=[name for name, row in plan['campaigns'].items() if 'REQUIRED' in json.dumps(row)],
    pack_executed=False, verify_executed=False, SDK_executed=False, tests_executed=False), indent=2))
