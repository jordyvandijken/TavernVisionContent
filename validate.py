#!/usr/bin/env python3
"""
Campaign JSON Validator

Validates all JSON files in the content/ directory against the schema.json file.
"""

import json
import sys
from pathlib import Path
from jsonschema import Draft7Validator

# Ensure emoji/Unicode output works on the default Windows console codepage.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

def load_schema():
    """Load the JSON schema from schema.json"""
    try:
        with open('schema.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: schema.json not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in schema.json - {e}")
        sys.exit(1)

def validate_file(file_path, schema):
    """Validate a single JSON file against the schema"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create validator with format checking enabled
        validator = Draft7Validator(schema, format_checker=Draft7Validator.FORMAT_CHECKER)
        
        # Check for validation errors
        errors = list(validator.iter_errors(data))
        if errors:
            error_messages = []
            for error in errors:
                # Build path to the error location
                path = " -> ".join([str(p) for p in error.absolute_path]) if error.absolute_path else "root"
                error_messages.append(f"At '{path}': {error.message}")
            
            return False, "\n    ".join(error_messages)
        
        return True, None
    
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def main():
    """Main validation function"""
    print("🔍 Campaign JSON Validator")
    print("=" * 40)
    
    # Load schema
    schema = load_schema()
    print("✅ Schema loaded successfully")
    
    # Find all JSON files in content directory (recursively)
    content_dir = Path('content')
    if not content_dir.exists():
        print("❌ Error: content/ directory not found")
        sys.exit(1)
    
    json_files = [
        f for f in content_dir.glob('**/*.json')
        if f.name != 'channel.json'
    ]
    if not json_files:
        print("⚠️  Warning: No JSON files found in content/ directory")
        return
    
    print(f"📁 Found {len(json_files)} JSON file(s) to validate")
    print()
    
    # Validate each file
    valid_count = 0
    invalid_count = 0
    
    for file_path in sorted(json_files):
        relative_path = file_path.relative_to(content_dir)
        print(f"🔄 Validating {relative_path}...")
        is_valid, error_msg = validate_file(file_path, schema)
        
        if is_valid:
            print(f"  ✅ Valid")
            valid_count += 1
        else:
            print(f"  ❌ Invalid: {error_msg}")
            invalid_count += 1
        print()
    
    # Summary
    print("=" * 40)
    print(f"📊 Summary:")
    print(f"  ✅ Valid files: {valid_count}")
    print(f"  ❌ Invalid files: {invalid_count}")
    print(f"  📄 Total files: {len(json_files)}")
    
    if invalid_count > 0:
        print(f"\n⚠️  {invalid_count} file(s) failed validation")
        sys.exit(1)
    else:
        print("\n🎉 All files are valid!")

if __name__ == "__main__":
    main()