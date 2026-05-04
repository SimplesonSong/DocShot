"""DocShot package."""

from .converter import PdfToWordFastError, WordToPdfError, convert_word_to_pdf, pdf_to_word_fast
from .pdf_to_images import ConversionCancelledError, PdfToImagesError, convert_pdf_to_images
from .pdf_to_word_ocr import PdfToWordOcrError, pdf_to_word_ocr
from .word_to_images import WordToImagesError, convert_word_to_images

__all__ = [
    "WordToPdfError",
    "PdfToWordFastError",
    "convert_word_to_pdf",
    "pdf_to_word_fast",
    "PdfToImagesError",
    "ConversionCancelledError",
    "convert_pdf_to_images",
    "PdfToWordOcrError",
    "pdf_to_word_ocr",
    "WordToImagesError",
    "convert_word_to_images",
]
