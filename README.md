# TavernVision Content

This repository contains structured campaign data for TavernVision, a D&D content platform.

## Structure

-   `schema.json` - JSON Schema that defines the structure for campaign files
-   `content/` - Directory containing campaign JSON files

## Campaign JSON Format

Each campaign file contains:

-   **Campaign metadata**: title, description, thumbnail URL
-   **Episodes**: Array of episodes with YouTube IDs and descriptions
-   **Segments** (optional): Time-stamped segments with skip/next actions
-   **People** (optional): Cast and characters involved

## Verification

To validate a campaign JSON file against the schema:

### Using VS Code

1. Install the "JSON Schema" extension
2. Open any `.json` file in the `content/` directory
3. Validation errors will be highlighted automatically

### Using Node.js

```bash
npm install ajv
node -e "
const Ajv = require('ajv');
const fs = require('fs');
const ajv = new Ajv();
const schema = JSON.parse(fs.readFileSync('schema.json'));
const data = JSON.parse(fs.readFileSync('content/critical-campaign-1.json'));
const valid = ajv.validate(schema, data);
console.log(valid ? 'Valid!' : ajv.errors);
"
```

### Using Python

```bash
pip install jsonschema
python -c "
import json
from jsonschema import validate
with open('schema.json') as f: schema = json.load(f)
with open('content/critical-campaign-1.json') as f: data = json.load(f)
validate(data, schema)
print('Valid!')
"
```

## Example Structure

```json
{
  "title": "Campaign Name",
  "description": "Campaign description",
  "thumbnail": "https://example.com/thumb.jpg",
  "episodes": [
    {
      "title": "Episode 1",
      "youtubeid": "dQw4w9WgXcQ",
      "description": "Episode description",
      "segments": [
        {
            "title": "Break",
            "start": "h:mm:ss",
            "end": "h:mm:ss",
            "action": "skip" || "next" || ""
        }
      ],
      "people": [
        {
            "name": "Someone",
            "role": "Dungeon Master"
        }
      ]
    }
  ]
}
```
