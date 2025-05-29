import io

import fitz  # PyMuPDF
from PIL import Image


def compress_pdf(  # cross‑platform
    input_path: str,
    output_path: str,
    target_dpi: int = 100,  # if you have meaningful DPI metadata
    jpeg_quality: int = 70,
):
    """
    - Extract each image
    - (Optionally) downsample it via Pillow
    - Re‑encode as JPEG at jpeg_quality
    - Replace in PDF with Page.replace_image (updates all PDF headers)
    - Deflate & clean up on save
    """
    doc = fitz.open(input_path)
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # Convert Pixmap → PIL.Image
            mode = "RGBA" if pix.alpha else "RGB"
            pil = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

            # Convert RGBA to RGB by removing alpha channel
            if mode == "RGBA":
                background = Image.new("RGB", pil.size, (255, 255, 255))
                background.paste(pil, mask=pil.split()[3])  # Use alpha channel as mask
                pil = background

            # (Optional) downsample by DPI ratio if original DPI known:
            if target_dpi and hasattr(pix, "xres") and pix.xres > 0:
                scale = target_dpi / pix.xres
                if scale != 1:
                    new_size = (int(pix.width * scale), int(pix.height * scale))
                    pil = pil.resize(new_size, Image.LANCZOS)

            # Encode to JPEG in memory
            buf = io.BytesIO()
            pil.save(buf, "JPEG", quality=jpeg_quality)
            jpeg_bytes = buf.getvalue()
            buf.close()

            # **Replace** the image stream & headers in one go
            page.replace_image(
                xref, stream=jpeg_bytes
            )  #  [oai_citation_attribution:0‡PyMuPDF](https://pymupdf.readthedocs.io/en/latest/page.html?utm_source=chatgpt.com)

            pix = None  # free resources

    # Save, removing unused objects and deflating other streams
    doc.save(
        output_path,
        garbage=4,  # drop unused objects
        deflate=True,  # recompress non‑image streams losslessly
    )
    doc.close()
