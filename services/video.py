import logging
import shutil
import subprocess
import threading
from pathlib import Path

from core.config import settings

logger = logging.getLogger("uvicorn.error")

# Une seule compression à la fois : ffmpeg utilise déjà tous les cœurs du processeur
_compression_lock = threading.Lock()


def ffmpeg_executable() -> str | None:
    if settings.ffmpeg_path:
        return settings.ffmpeg_path
    if found := shutil.which("ffmpeg"):
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # paquet absent ou binaire introuvable
        return None


def _scale_filter(max_dimension: int) -> str:
    """Réduit le plus petit côté à max_dimension sans jamais agrandir (dimensions paires pour H.264)."""
    side = f"trunc(min({max_dimension},{{}})/2)*2"
    return (
        f"scale=w='if(gte(iw,ih),-2,{side.format('iw')})'"
        f":h='if(gte(iw,ih),{side.format('ih')},-2)'"
    )


def _codec_args(extension: str) -> list[str]:
    if extension == ".webm":
        return [
            "-c:v", "libvpx-vp9", "-crf", "36", "-b:v", "0", "-row-mt", "1",
            "-deadline", "good", "-cpu-used", "4",
            "-c:a", "libopus", "-b:a", "96k",
        ]
    return [
        "-c:v", "libx264", "-preset", "veryfast", "-crf", str(settings.video_crf),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
    ]


def compress_video(source: Path) -> Path | None:
    """Compresse la vidéo dans un fichier voisin et retourne son chemin.

    Retourne None si ffmpeg est indisponible, si la compression échoue
    ou si le résultat n'est pas plus léger que l'original.
    """
    executable = ffmpeg_executable()
    if executable is None:
        logger.warning("ffmpeg introuvable : la vidéo %s est conservée sans compression.", source.name)
        return None

    target = source.with_name(f"{source.stem}.compressing{source.suffix}")
    command = [
        executable, "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source),
        "-vf", _scale_filter(settings.video_max_dimension),
        *_codec_args(source.suffix.lower()),
        str(target),
    ]

    try:
        with _compression_lock:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=settings.video_compression_timeout_seconds,
            )
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.warning("Compression de %s interrompue : %s", source.name, exc)
        target.unlink(missing_ok=True)
        return None

    if result.returncode != 0 or not target.exists():
        logger.warning("Compression de %s échouée : %s", source.name, result.stderr.strip()[-500:])
        target.unlink(missing_ok=True)
        return None

    if target.stat().st_size >= source.stat().st_size:
        target.unlink(missing_ok=True)
        return None
    return target
