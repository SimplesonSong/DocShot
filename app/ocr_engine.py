"""PaddleOCR engine wrapper for minimal CLI testing."""

import os
from pathlib import Path
from typing import Any


class OcrEngine:
    def __init__(self):
        # Model files may be downloaded and initialized on first run, so startup can be slow.
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")
        os.environ.setdefault("FLAGS_enable_pir_api", "0")
        # Reduce chance of auxiliary runtime windows/process noise on Windows.
        os.environ.setdefault("FLAGS_use_mkldnn", "0")
        os.environ.setdefault("FLAGS_allocator_strategy", "naive_best_fit")
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
        os.environ.setdefault("PADDLEOCR_USE_MP", "False")
        os.environ.setdefault("PADDLE_PDX_MODEL_SOURCE", "BOS")

        import paddleocr
        from paddleocr import PaddleOCR

        version = str(getattr(paddleocr, "__version__", ""))
        major = int(version.split(".")[0]) if version and version[0].isdigit() else 0
        if major >= 3:
            raise RuntimeError(
                "Detected paddleocr>=3, which is incompatible with current DocShot OCR runtime. "
                "Please install paddleocr==2.7.3 and paddlepaddle==2.6.2, then rebuild the package."
            )

        init_errors: list[str] = []
        candidates = [
            {
                "use_angle_cls": False,
                "lang": "ch",
                "use_gpu": False,
                "enable_mkldnn": False,
                "use_mp": False,
            },
            {
                "use_angle_cls": True,
                "lang": "ch",
                "use_gpu": False,
                "enable_mkldnn": False,
                "use_mp": False,
            },
            {"use_angle_cls": False, "lang": "ch", "use_gpu": False, "enable_mkldnn": False},
            {"use_angle_cls": True, "lang": "ch", "use_gpu": False, "enable_mkldnn": False},
            {"use_angle_cls": False, "lang": "ch", "use_gpu": False},
            {"use_angle_cls": True, "lang": "ch", "use_gpu": False},
            {"lang": "ch", "use_gpu": False},
            {"use_angle_cls": True, "lang": "ch"},
            {"lang": "ch"},
        ]

        self._ocr = None
        for kwargs in candidates:
            try:
                self._ocr = PaddleOCR(**kwargs)
                break
            except Exception as exc:  # pragma: no cover - depends on local PaddleOCR version
                init_errors.append(f"kwargs={kwargs}, error={exc}")

        if self._ocr is None:
            detail = " | ".join(init_errors)
            raise RuntimeError(f"Failed to initialize PaddleOCR with compatible arguments. {detail}")

    def recognize_image(self, image_path: str) -> list[str]:
        image = Path(image_path)
        if not image.exists():
            raise FileNotFoundError(f"Image file does not exist: {image}")

        result = None
        ocr_errors: list[str] = []
        for kwargs in ({"cls": True}, {}):
            try:
                result = self._ocr.ocr(str(image), **kwargs)
                break
            except Exception as exc:
                ocr_errors.append(f"kwargs={kwargs}, error={exc}")

        if result is None:
            detail = " | ".join(ocr_errors)
            raise RuntimeError(f"Failed to run OCR on image: {image}. {detail}")

        return self._extract_texts(result)

    def _extract_texts(self, result: Any) -> list[str]:
        texts: list[str] = []

        def add_text(value: Any) -> None:
            if isinstance(value, str):
                stripped = value.strip()
                if stripped:
                    texts.append(stripped)

        def walk(node: Any) -> None:
            if node is None:
                return

            if isinstance(node, str):
                return

            if isinstance(node, dict):
                rec_texts = node.get("rec_texts")
                if isinstance(rec_texts, list):
                    for item in rec_texts:
                        add_text(item)

                text_value = node.get("text")
                add_text(text_value)
                recs = node.get("rec")
                if recs is not None:
                    walk(recs)
                res = node.get("result")
                if res is not None:
                    walk(res)
                return

            if isinstance(node, (list, tuple)):
                if len(node) >= 2:
                    rec = node[1]
                    if isinstance(rec, (list, tuple)) and rec:
                        add_text(rec[0])
                    elif isinstance(rec, dict):
                        add_text(rec.get("text"))
                for item in node:
                    walk(item)
                return

        walk(result)

        deduped: list[str] = []
        seen: set[str] = set()
        for t in texts:
            if t not in seen:
                seen.add(t)
                deduped.append(t)

        return deduped
