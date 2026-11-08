"""Batch converter script using Docling to extract clean Markdown from HTML SEC 10-K filings.

Converts all .htm/.html files under data/downloads/<year>/ into matching
clean Markdown files under data/markdown/<year>/<filename>.md.
"""

from pathlib import Path
import sys
import time

from docling.document_converter import DocumentConverter


def convert_all(downloads_dir: Path, markdown_dir: Path) -> None:
    if not downloads_dir.exists():
        print(f"Error: {downloads_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # Collect all htm/html files in downloads
    htm_files = sorted(
        [p for p in downloads_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".htm", ".html"}]
    )

    if not htm_files:
        print(f"No .htm or .html files found in {downloads_dir}")
        return

    print(f"Found {len(htm_files)} HTML filing(s) to convert.")
    markdown_dir.mkdir(parents=True, exist_ok=True)

    converter = DocumentConverter()

    start_total = time.time()
    success_count = 0
    failed_count = 0

    for idx, file_path in enumerate(htm_files, 1):
        rel_path = file_path.relative_to(downloads_dir)
        target_path = (markdown_dir / rel_path).with_suffix(".md")
        target_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n[{idx}/{len(htm_files)}] Converting {rel_path} -> {target_path.relative_to(markdown_dir.parent)}")
        t0 = time.time()

        try:
            result = converter.convert(file_path)
            md_content = result.document.export_to_markdown()

            target_path.write_text(md_content, encoding="utf-8")
            elapsed = time.time() - t0
            print(f"  ✓ Finished in {elapsed:.2f}s ({len(md_content):,} chars written)")
            success_count += 1
        except Exception as err:
            elapsed = time.time() - t0
            print(f"  ✗ Failed after {elapsed:.2f}s: {err}", file=sys.stderr)
            failed_count += 1

    total_time = time.time() - start_total
    print(f"\n==========================================")
    print(f"Conversion complete in {total_time:.1f}s!")
    print(f"Successfully converted: {success_count}/{len(htm_files)}")
    if failed_count > 0:
        print(f"Failed: {failed_count}/{len(htm_files)}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    downloads = base_dir / "data" / "downloads"
    markdown = base_dir / "data" / "markdown"
    convert_all(downloads, markdown)

