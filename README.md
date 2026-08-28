# TavernVision Content

This repository contains structured campaign data for TavernVision, a D&D content platform.

## Structure

-   `schema.json` - JSON Schema that defines the structure for campaign files
-   `content/` - Directory containing campaign JSON files

## Campaign JSON Format

Each campaign file contains:

-   **Campaign metadata**: title, description, thumbnail URL, status
-   **Episodes**: Array of episodes with YouTube IDs, descriptions, and upload dates
-   **Segments** (optional): Time-stamped segments with skip/next actions
-   **People** (optional): Cast and characters involved

In addition to campaign files, each subfolder under `content/` may contain a
`channel.json` holding channel metadata (e.g. `name` and `channelUrl`). These
files are not campaigns and are not validated against `schema.json`.

## Verification

To validate all campaign JSON files against the schema, run:

```powershell
python .\validate.py
```

This script checks every campaign file in `content/` against `schema.json` and
reports any validation errors. `channel.json` files are skipped.

## Fix Missing Episode Metadata

`fix.py` scans campaign files under `content/` and fills missing episode
metadata from YouTube (title and `uploadDate`) for episodes that have a
`youtubeid`:

```powershell
python .\fix.py
```

Useful options:

```powershell
python .\fix.py --content-dir content --dry-run
```

-   `--content-dir`: directory to scan (default: `content`)
-   `--dry-run`: preview changes without writing them

## Example Structure

```json
{
  "title": "Campaign Name",
  "description": "Campaign description",
  "thumbnail": "https://example.com/thumb.jpg",
  "status": "inProgress",
  "episodes": [
    {
      "title": "Episode 1",
      "youtubeid": "dQw4w9WgXcQ",
      "description": "Episode description",
      "uploadDate": "2024-01-01",
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
