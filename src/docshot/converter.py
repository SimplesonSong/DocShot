"""Document conversion utilities."""

import io
import sys
from contextlib import contextmanager
from pathlib import Path

_ALLOWED_SUFFIXES = {".doc", ".docx"}
_PDF_SUFFIX = ".pdf"


class WordToPdfError(Exception):
    """Raised when Word to PDF conversion fails."""


class PdfToWordFastError(Exception):
    """Raised when fast PDF to Word conversion fails."""


@contextmanager
def _safe_std_streams():
    """Ensure stdout/stderr are writable for docx2pdf in windowed apps."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def convert_word_to_pdf(word_path: str, pdf_path: str) -> str:
    """Convert a Word document (.doc/.docx) to PDF and return the output path."""
    source = Path(word_path)
    target = Path(pdf_path)

    if not source.exists():
        raise FileNotFoundError(f"Word file does not exist: {source}")

    if source.suffix.lower() not in _ALLOWED_SUFFIXES:
        allowed = ", ".join(sorted(_ALLOWED_SUFFIXES))
        raise ValueError(
            f"Unsupported file extension: {source.suffix or '<none>'}. "
            f"Supported extensions are: {allowed}"
        )

    target_parent = target.parent
    if not target_parent.exists():
        target_parent.mkdir(parents=True, exist_ok=True)

    try:
        from docx2pdf import convert

        with _safe_std_streams():
            convert(str(source), str(target))
    except Exception as exc:  # pragma: no cover - depends on local Word environment
        raise WordToPdfError(
            f"Failed to convert Word to PDF. source='{source}', target='{target}', error='{exc}'"
        ) from exc

    return str(target)


def pdf_to_word_fast(pdf_path: str, output_docx_path: str) -> str:
    """Convert a normal PDF to DOCX using pdf2docx and return output path."""
    source = Path(pdf_path)
    target = Path(output_docx_path)

    if not source.exists():
        raise FileNotFoundError(f"PDF file does not exist: {source}")

    if source.suffix.lower() != _PDF_SUFFIX:
        raise ValueError(
            f"Unsupported file extension: {source.suffix or '<none>'}. "
            f"Expected extension: {_PDF_SUFFIX}"
        )

    target_parent = target.parent
    if not target_parent.exists():
        target_parent.mkdir(parents=True, exist_ok=True)

    pdf_converter = None
    try:
        from pdf2docx import Converter

        pdf_converter = Converter(str(source))
        pdf_converter.convert(str(target))
    except Exception as exc:
        raise PdfToWordFastError(
            f"Failed to convert PDF to Word (fast mode). "
            f"source='{source}', target='{target}', error='{exc}'"
        ) from exc
    finally:
        if pdf_converter is not None:
            try:
                pdf_converter.close()
            except Exception:
                pass

    return str(target)
