"""PDF to image conversion utilities."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

_ALLOWED_FORMATS = {"png", "jpg"}


class PdfToImagesError(Exception):
    """Raised when PDF to image conversion fails."""


class ConversionCancelledError(Exception):
    """Raised when user cancels conversion."""


def convert_pdf_to_images(
    pdf_path: str,
    output_dir: str,
    image_format: str = "png",
    zoom: float = 2.0,
    status_callback: Callable[[str], None] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> list[str]:
    """Convert each PDF page to an image and return exported file paths."""
    source = Path(pdf_path)
    out_dir = Path(output_dir)

    if not source.exists():
        raise FileNotFoundError(f"PDF file does not exist: {source}")

    fmt = image_format.lower()
    if fmt not in _ALLOWED_FORMATS:
        allowed = ", ".join(sorted(_ALLOWED_FORMATS))
        raise ValueError(
            f"Unsupported image format: {image_format}. Supported formats are: {allowed}"
        )

    if zoom <= 0:
        raise ValueError(f"zoom must be greater than 0, got: {zoom}")

    out_dir.mkdir(parents=True, exist_ok=True)

    doc = None
    exported_paths: list[str] = []

    try:
        import fitz

        doc = fitz.open(str(source))
        matrix = fitz.Matrix(zoom, zoom)
        total_pages = len(doc)

        for idx, page in enumerate(doc, start=1):
            if is_cancelled is not None and is_cancelled():
                raise ConversionCancelledError("Conversion cancelled by user.")

            if status_callback is not None:
                status_callback(f"正在导出第 {idx} 页")

            filename = f"page_{idx:03d}.{fmt}"
            output_path = out_dir / filename
            pixmap = page.get_pixmap(matrix=matrix)
            pixmap.save(str(output_path))
            exported_paths.append(str(output_path))

            if progress_callback is not None:
                progress_callback(idx, total_pages)
    except ConversionCancelledError:
        raise
    except Exception as exc:  # pragma: no cover - depends on local files/environment
        raise PdfToImagesError(
            f"Failed to convert PDF to images. source='{source}', output_dir='{out_dir}', "
            f"format='{fmt}', zoom='{zoom}', error='{exc}'"
        ) from exc
    finally:
        if doc is not None:
            doc.close()

    return exported_paths
