# SHACL Validation Guide

## Quick Start

1. **Install pySHACL**:
   ```bash
   pip install pyshacl
   # or
   conda install -c conda-forge pyshacl
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x *.sh
   ```

3. **Run the test suite**:
   ```bash
   ./run-tests.sh
   ```

## Manual Validation Commands

### Basic validation:
```bash
pyshacl -s actions-shapes.ttl -d your-data.ttl
```

### Validation with detailed output:
```bash
pyshacl -s actions-shapes.ttl -d your-data.ttl -f turtle -v
```

### Save validation report:
```bash
pyshacl -s actions-shapes.ttl -d your-data.ttl -f turtle > validation-report.ttl
```

## Test Files

| File | Purpose | Expected Result |
|------|---------|----------------|
| `test-data-valid.ttl` | Valid examples | ✅ Should pass |
| `test-data-invalid.ttl` | Invalid examples | ❌ Should fail |

## Test Scripts

| Script | Purpose |
|--------|---------|
| `run-tests.sh` | Quick test suite runner |
| `validate-detailed.sh` | Detailed individual constraint testing |
| `setup-validation.sh` | Installation helper |

## Common Validation Errors

### 1. **Depth Violations**
```turtle
# ❌ Wrong: Root action with depth 1
actions:root a actions:RootAction ;
    actions:depth 1 .  # Should be 0

# ✅ Correct:
actions:root a actions:RootAction ;
    actions:depth 0 .
```

### 2. **Missing Required Properties**
```turtle
# ❌ Wrong: Missing priority and state
actions:action1 a actions:RootAction ;
    actions:depth 0 .

# ✅ Correct:
actions:action1 a actions:RootAction ;
    actions:depth 0 ;
    actions:priority 1 ;
    actions:state actions:NotStarted .
```

### 3. **Invalid Parent-Child Relationships**
```turtle
# ❌ Wrong: Child without parent
actions:child a actions:ChildAction ;
    actions:depth 2 .  # Missing parentAction

# ✅ Correct:
actions:child a actions:ChildAction ;
    actions:depth 2 ;
    actions:parentAction actions:parent .
```

### 4. **Context Format**
```turtle
# ❌ Wrong: Context without @
actions:action a actions:RootAction ;
    actions:context "computer" .

# ✅ Correct:
actions:action a actions:RootAction ;
    actions:context "@computer" .
```

### 5. **Priority Range**
```turtle
# ❌ Wrong: Priority outside 1-4 range
actions:action a actions:RootAction ;
    actions:priority 5 .  # Must be 1-4

# ✅ Correct:
actions:action a actions:RootAction ;
    actions:priority 1 .  # 1-4 for Eisenhower matrix
```

## Exit Codes

- **0**: Validation passed (data conforms to shapes)
- **1**: Validation failed (constraint violations found)
- **2**: Error in shapes or data parsing

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Validate SHACL
  run: |
    pip install pyshacl
    pyshacl -s actions-shapes.ttl -d production-data.ttl
```

## Troubleshooting

### Common Issues:

1. **"No module named 'pyshacl'"**
   - Solution: `pip install pyshacl`

2. **"Permission denied" on scripts**
   - Solution: `chmod +x *.sh`

3. **"File not found"**
   - Ensure all `.ttl` files are in the same directory
   - Check file paths in commands

### Debug Mode:
```bash
pyshacl -s actions-shapes.ttl -d your-data.ttl -v --debug
```

## Advanced Usage

### Custom Output Formats:
```bash
# JSON-LD output
pyshacl -s shapes.ttl -d data.ttl -f json-ld

# N-Triples output  
pyshacl -s shapes.ttl -d data.ttl -f nt

# Human-readable text
pyshacl -s shapes.ttl -d data.ttl -f human
```

### Validation with Inference:
```bash
pyshacl -s shapes.ttl -d data.ttl --inference rdfs
```
