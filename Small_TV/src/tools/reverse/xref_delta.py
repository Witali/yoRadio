"""Store bounded analysis changes without duplicating a complete address graph."""
import copy
import hashlib
import json


def digest(value):
    """Hash parsed graph content independently of JSON whitespace and line endings."""
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def key(row):
    """Keep a function's namespace and numeric guest entry unambiguous."""
    return row['space'],row['entry']


def difference(before,after):
    """Record additions/replacements only; removing old analysis requires separate review."""
    assert set(before)==set(after)
    old={key(r):r for r in before['functions']};new={key(r):r for r in after['functions']}
    assert len(old)==len(before['functions']) and len(new)==len(after['functions']) and set(old)<=set(new)
    old_gp={r['from']:r for r in before['gp_accesses']};new_gp={r['from']:r for r in after['gp_accesses']}
    assert set(old_gp)<=set(new_gp)
    return dict(schema_version=1,before_sha256=digest(before),after_sha256=digest(after),
        metadata={k:v for k,v in after.items() if k not in ('functions','gp_accesses') and before[k]!=v},
        functions=[r for r in after['functions'] if old.get(key(r))!=r],
        gp_accesses=[r for r in after['gp_accesses'] if old_gp.get(r['from'])!=r])


def apply(before,delta):
    """Reconstruct the exact parsed observation and verify its declared content digest."""
    assert delta['schema_version']==1 and digest(before)==delta['before_sha256']
    after=copy.deepcopy(before);after.update(delta['metadata'])
    functions={key(r):r for r in after['functions']};gp={r['from']:r for r in after['gp_accesses']}
    assert len({key(r) for r in delta['functions']})==len(delta['functions'])
    assert len({r['from'] for r in delta['gp_accesses']})==len(delta['gp_accesses'])
    functions.update({key(r):r for r in delta['functions']});gp.update({r['from']:r for r in delta['gp_accesses']})
    assert all(k[0]=='ram' for k in functions),'This profile uses one guest memory namespace'
    after['functions']=sorted(functions.values(),key=lambda r:int(r['entry'],0))
    after['gp_accesses']=sorted(gp.values(),key=lambda r:int(r['from'],0))
    assert digest(after)==delta['after_sha256']
    return after
