# dia_modal.py
import io

import modal

app = modal.App("podcaist")
image = (
    modal.Image.debian_slim()
    .apt_install("git", "ffmpeg", "libsndfile1")
    .pip_install(
        "soundfile",
        "git+https://github.com/nari-labs/dia.git",
        "kokoro",
    )
    # mount your local podcast code so synthesize() can import it
    .add_local_python_source("podcaist")
    # also satisfy the module name Modal warned about
    .add_local_python_source("_remote_module_non_scriptable")
)
