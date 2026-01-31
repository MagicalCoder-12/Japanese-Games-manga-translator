import pyautogui
import cv2
import numpy as np
import pyperclip
from manga_ocr import MangaOcr

manga_ocr = MangaOcr()

def normalize_for_translation(text: str) -> str:
    """
    Fix OCR artifacts WITHOUT changing Japanese meaning or structure.
    Safe for translators (LLMs, NMT, etc).
    """

    fixes = {
        "．．．": "・・・",
        "...": "・・・",
        "？！」": "！？",
        "？」": "！？",
        "?!": "！？",
        "!?": "！？",
        "»": "",
        "«": "",
    }

    for bad, good in fixes.items():
        text = text.replace(bad, good)

    # Remove accidental spaces inside JP sentences
    text = text.replace("  ", " ").strip()

    return text

def extract_japanese_text(region):
    """
    MangaOCR-based extraction, meaning-preserving.
    """

    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Save temp image (MangaOCR requires path or PIL)
    temp_path = "_ocr_tmp.png"
    cv2.imwrite(temp_path, img)

    try:
        text = manga_ocr(temp_path)
        text = text.strip()
        text = normalize_for_translation(text)
        return text

    except Exception as e:
        print(f"❌ MangaOCR failed: {e}")
        return ""

def copy_for_translation(text):
    if not text:
        print("❌ No text extracted")
        return

    pyperclip.copy(text)
    print("📋 Japanese text copied (structure preserved)")
    print("-" * 50)
    print(text)
    print("-" * 50)
