"""Word to image end-to-end conversion workflow."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from .converter import convert_word_to_pdf
from .pdf_to_images import ConversionCancelledError, convert_pdf_to_images

_QUALITY_TO_ZOOM = {
    "normal": 1.5,
    "high": 2.0,
    "ultra": 3.0,
}


class WordToImagesError(Exception):
    """Raised when Word to image workflow fails."""


def _build_unique_output_dir(word_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = word_path.stem
    candidate = output_dir / f"{base_name}_images"
    if not candidate.exists():
        candidate.mkdir(parents=True, exist_ok=False)
        return candidate

    index = 1
    while True:
        candidate = output_dir / f"{base_name}_images_{index}"
        if not candidate.exists():
            candidate.mkdir(parents=True, exist_ok=False)
            return candidate
        index += 1


def convert_word_to_images(
    word_path: str,
    output_dir: str,
    image_format: str = "png",
    quality_level: str = "high",
    status_callback: Callable[[str], None] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    is_cancelled: Callable[[], bool] | None = None,
) -> list[str]:
    """Convert a Word document to images and return all exported file paths."""
    source = Path(word_path)
    out_root = Path(output_dir)

    quality_key = quality_level.lower()
    if quality_key not in _QUALITY_TO_ZOOM:
        allowed = ", ".join(_QUALITY_TO_ZOOM.keys())
        raise ValueError(
            f"Unsupported quality_level: {quality_level}. Supported levels are: {allowed}"
        )

    try:
        final_output_dir = _build_unique_output_dir(source, out_root)

        if progress_callback is not None:
            progress_callback(10, 100)

        with TemporaryDirectory(prefix="docshot_") as temp_dir:
            temp_pdf = Path(temp_dir) / f"{source.stem}.pdf"

            if status_callback is not None:
                status_callback("正在转换 Word 为 PDF")

            convert_word_to_pdf(str(source), str(temp_pdf))

            if is_cancelled is not None and is_cancelled():
                raise ConversionCancelledError("Conversion cancelled by user.")

            if progress_callback is not None:
                progress_callback(30, 100)

            def page_progress(current: int, total: int) -> None:
                if progress_callback is None:
                    return
                if total <= 0:
                    progress_callback(90, 100)
                    return
                # Map page export progress to 30% -> 100%
                mapped = 30 + int((current / total) * 70)
                progress_callback(min(mapped, 100), 100)

            image_paths = convert_pdf_to_images(
                pdf_path=str(temp_pdf),
                output_dir=str(final_output_dir),
                image_format=image_format,
                zoom=_QUALITY_TO_ZOOM[quality_key],
                status_callback=status_callback,
                progress_callback=page_progress,
                is_cancelled=is_cancelled,
            )

            if status_callback is not None:
                status_callback("转换完成")
            if progress_callback is not None:
                progress_callback(100, 100)

            return image_paths
    except ConversionCancelledError:
        raise
    except Exception as exc:
        raise WordToImagesError(
            f"Failed to convert Word to images. word_path='{source}', output_dir='{out_root}', "
            f"image_format='{image_format}', quality_level='{quality_level}', error='{exc}'"
        ) from exc
