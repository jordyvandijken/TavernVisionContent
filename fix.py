#!/usr/bin/env python3
"""
Campaign JSON fixer.

Scans campaign files under content/ and fills missing episode metadata from YouTube,
but only when an episode has a youtubeid.

Fix rules:
- If title is missing/empty, use the YouTube video title.
- If uploadDate is missing/empty, use the YouTube upload date in YYYY-MM-DD format.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


YOUTUBE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")


@dataclass
class VideoMetadata:
	title: str | None
	upload_date: str | None


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Fix missing episode title/uploadDate from YouTube metadata"
	)
	parser.add_argument(
		"--content-dir",
		type=Path,
		default=Path("content"),
		help="Directory containing campaign JSON files (default: content)",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Show planned changes without writing files",
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help="Print extra diagnostics",
	)
	return parser.parse_args()


def is_missing_string(value: Any) -> bool:
	return not isinstance(value, str) or not value.strip()


def normalize_upload_date(raw: str | None) -> str | None:
	if not raw:
		return None
	if len(raw) == 8 and raw.isdigit():
		try:
			return datetime.strptime(raw, "%Y%m%d").strftime("%Y-%m-%d")
		except ValueError:
			return None
	if len(raw) == 10:
		try:
			return datetime.strptime(raw, "%Y-%m-%d").strftime("%Y-%m-%d")
		except ValueError:
			return None
	return None


def fetch_video_metadata(youtubeid: str) -> VideoMetadata | None:
	# Defer optional dependency import so argparse/help still works without yt-dlp.
	try:
		import yt_dlp  # type: ignore
	except ImportError:
		print("❌ Missing dependency: yt-dlp")
		print("   Install with: python -m pip install yt-dlp")
		return None

	url = f"https://www.youtube.com/watch?v={youtubeid}"
	opts = {
		"quiet": True,
		"no_warnings": True,
		"skip_download": True,
		"extract_flat": True,
	}

	try:
		with yt_dlp.YoutubeDL(opts) as ydl:
			info = ydl.extract_info(url, download=False)
	except Exception as exc:  # pragma: no cover
		print(f"  ⚠️ Could not fetch metadata for {youtubeid}: {exc}")
		return None

	if not isinstance(info, dict):
		return None

	title = info.get("title") if isinstance(info.get("title"), str) else None
	upload_date = normalize_upload_date(
		info.get("upload_date") if isinstance(info.get("upload_date"), str) else None
	)
	return VideoMetadata(title=title, upload_date=upload_date)


def fix_campaign_file(
	file_path: Path,
	*,
	dry_run: bool,
	verbose: bool,
	metadata_cache: dict[str, VideoMetadata | None],
) -> tuple[bool, int]:
	try:
		data = json.loads(file_path.read_text(encoding="utf-8"))
	except json.JSONDecodeError as exc:
		print(f"❌ {file_path}: invalid JSON ({exc})")
		return False, 0

	episodes = data.get("episodes")
	if not isinstance(episodes, list):
		if verbose:
			print(f"⚠️ {file_path}: missing or invalid episodes array")
		return False, 0

	changed = False
	fix_count = 0

	for idx, episode in enumerate(episodes):
		if not isinstance(episode, dict):
			continue

		youtubeid = episode.get("youtubeid")
		if not isinstance(youtubeid, str) or not YOUTUBE_ID_RE.match(youtubeid):
			continue

		needs_title = is_missing_string(episode.get("title"))
		needs_date = is_missing_string(episode.get("uploadDate"))

		if not (needs_title or needs_date):
			continue

		if youtubeid not in metadata_cache:
			metadata_cache[youtubeid] = fetch_video_metadata(youtubeid)

		meta = metadata_cache[youtubeid]
		if meta is None:
			continue

		if needs_title and meta.title:
			episode["title"] = meta.title
			changed = True
			fix_count += 1
			print(f"  ✅ episode[{idx}] filled title from youtubeid {youtubeid}")

		if needs_date and meta.upload_date:
			episode["uploadDate"] = meta.upload_date
			changed = True
			fix_count += 1
			print(f"  ✅ episode[{idx}] filled uploadDate from youtubeid {youtubeid}")

	if changed and not dry_run:
		file_path.write_text(
			json.dumps(data, indent=4, ensure_ascii=False) + "\n",
			encoding="utf-8",
		)

	return changed, fix_count


def main() -> None:
	args = parse_args()
	content_dir: Path = args.content_dir

	if not content_dir.exists():
		print(f"❌ Content directory not found: {content_dir}")
		sys.exit(1)

	json_files = sorted(content_dir.rglob("*.json"))
	if not json_files:
		print("⚠️ No JSON files found")
		return

	print("🛠️ Campaign Metadata Fixer")
	print("=" * 40)
	print(f"Found {len(json_files)} JSON files")
	if args.dry_run:
		print("Running in dry-run mode (no files will be written)")
	print()

	metadata_cache: dict[str, VideoMetadata | None] = {}
	files_changed = 0
	total_fixes = 0

	for file_path in json_files:
		print(f"🔄 Checking {file_path}...")
		changed, fix_count = fix_campaign_file(
			file_path,
			dry_run=args.dry_run,
			verbose=args.verbose,
			metadata_cache=metadata_cache,
		)
		if changed:
			files_changed += 1
		total_fixes += fix_count

	print()
	print("=" * 40)
	print(f"Files changed: {files_changed}")
	print(f"Fields fixed:  {total_fixes}")


if __name__ == "__main__":
	main()
