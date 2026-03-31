import yt_dlp


def scrape_profile_reels(profile_url: str, max_results: int = 20) -> list[dict]:
    """Scrape reels from a Facebook profile/page URL.

    Returns a list of dicts with: url, title, view_count, like_count, duration, thumbnail.
    Sorted by view_count descending (best performing first).
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "playlistend": max_results,
        "ignoreerrors": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        },
    }

    # Try appending /reels if not already there
    urls_to_try = [profile_url]
    if "/reels" not in profile_url:
        clean = profile_url.rstrip("/")
        urls_to_try.append(f"{clean}/reels")
        urls_to_try.append(f"{clean}/videos")

    entries = []

    for url in urls_to_try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(url, download=False)

            if result and "entries" in result:
                for entry in result["entries"]:
                    if entry is None:
                        continue
                    entries.append(
                        {
                            "url": entry.get("webpage_url") or entry.get("url", ""),
                            "title": entry.get("title", "Untitled"),
                            "view_count": entry.get("view_count") or 0,
                            "like_count": entry.get("like_count") or 0,
                            "duration": entry.get("duration") or 0,
                            "thumbnail": entry.get("thumbnail", ""),
                        }
                    )
                if entries:
                    break
        except Exception:
            continue

    # Deduplicate by URL
    seen = set()
    unique = []
    for e in entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique.append(e)

    # Sort by views descending
    unique.sort(key=lambda x: x["view_count"], reverse=True)

    return unique


def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS."""
    if not seconds:
        return "N/A"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def format_views(count: int) -> str:
    """Format view count into human readable."""
    if not count:
        return "N/A"
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)
