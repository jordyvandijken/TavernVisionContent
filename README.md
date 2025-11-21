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

To validate all campaign JSON files against the schema, run:

```powershell
python .\validate.py
```

This script checks every file in `content/` against `schema.json` and reports any validation errors.

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
