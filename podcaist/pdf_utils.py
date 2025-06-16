import io
import fitz          # PyMuPDF
from PIL import Image


def compress_pdf(
    input_path: str,
    output_path: str,
    *,
    target_dpi: int | None = 50,   # down-sample when image has DPI data
    max_dim_px: int = 800,         # absolute pixel cap for width/height
    jpeg_quality: int = 30,         # lower = smaller file / lower fidelity
    force_grayscale: bool = False,  # scan-like docs shrink dramatically
):
    """
    Lossily recompresses every raster image and removes non-content bloat.

    ▸ Images
        – Down-sample by target_dpi **or** to max_dim_px (whichever triggers).
        – Convert RGBA → RGB; optionally RGB → L (8-bit gray).
        – Re-encode to JPEG (quality = jpeg_quality).

    ▸ Structure clean-up
        – Deletes page annotations, file attachments, and XMP/Info metadata.

    Parameters
    ----------
    input_path, output_path : str
    target_dpi      : if the original image reports > target_dpi, it is scaled
                      down proportionally. Set None to ignore DPI metadata.
    max_dim_px      : upper bound on width *or* height after scaling.
    jpeg_quality    : JPEG quality (20–60 is usual; lower → smaller).
    force_grayscale : convert colour images to 8-bit gray when True.
    """
    doc = fitz.open(input_path)

    # -------- prune non-essential objects --------
    doc.set_metadata({})          # clears Info dictionary
    if hasattr(doc, "del_xml_metadata"):
        doc.del_xml_metadata()    # XMP (PyMuPDF ≥ 1.23)

    # attachments:
    for fname in list(getattr(doc, "embeddedFileNames", [])):
        doc.embeddedFileDel(fname)

    for page in doc:
        # delete annotations (comments, Acrobat mark-ups, etc.)
        for annot in list(page.annots() or []):
            page.delete_annot(annot)

        # -------- recompress every raster image on the page --------
        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            # ---------- pillow conversion ----------
            mode = "RGBA" if pix.alpha else "RGB"
            pil = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

            # flatten alpha → white background
            if mode == "RGBA":
                bg = Image.new("RGB", pil.size, "white")
                bg.paste(pil, mask=pil.split()[-1])
                pil = bg

            # optional grayscale
            if force_grayscale and pil.mode != "L":
                pil = pil.convert("L")

            # ---------- adaptive down-sampling ----------
            scale = 1.0
            if target_dpi and getattr(pix, "xres", 0) > target_dpi > 0:
                scale = target_dpi / pix.xres

            if max(pil.size) * scale > max_dim_px:
                scale = max_dim_px / max(pil.size)

            if scale < 1.0:  # resize only if we’re shrinking
                new_size = (int(pil.width * scale), int(pil.height * scale))
                # Ensure dimensions are at least 1 pixel
                new_size = (max(1, new_size[0]), max(1, new_size[1]))
                pil = pil.resize(new_size, Image.LANCZOS)

            # ---------- JPEG re-encode ----------
            buf = io.BytesIO()
            pil.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
            page.replace_image(xref, stream=buf.getvalue())
            buf.close()
            pix = None  # free C resources

    # ---------- final save ----------
    doc.save(
        output_path,
        garbage=4,     # remove unused & compress object streams
        deflate=True,  # lossless deflate of font & content streams
        incremental=False,
    )
    doc.close()