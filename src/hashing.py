# hashing.py – 雜湊函式與 CLI
"""cyber‑dojo 專案的雜湊工具。

支援演算法：
- sha256
- sha3_256
- blake2b  (digest_size = 32 → 256‑bit)
- blake3   (需 pip install blake3)

用法：
    python hashing.py string "hello"      --algo sha256
    python hashing.py file   README.md    --algo blake3
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from enum import Enum
from pathlib import Path
from typing import Literal, Union

try:
    import blake3  # type: ignore
    _HAS_BLAKE3 = True
except ModuleNotFoundError:
    _HAS_BLAKE3 = False


class Algo(str, Enum):
    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"
    BLAKE3 = "blake3"

    @classmethod
    def list(cls) -> list[str]:
        algos = [cls.SHA256.value, cls.SHA3_256.value, cls.BLAKE2B.value]
        if _HAS_BLAKE3:
            algos.append(cls.BLAKE3.value)
        return algos


# ---------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------
def _new_hasher(algo: Algo):
    if algo == Algo.SHA256:
        return hashlib.sha256()
    if algo == Algo.SHA3_256:
        return hashlib.sha3_256()
    if algo == Algo.BLAKE2B:
        return hashlib.blake2b(digest_size=32)
    if algo == Algo.BLAKE3:
        if not _HAS_BLAKE3:  # pragma: no cover
            raise RuntimeError("blake3 module not installed; `pip install blake3`")
        return blake3.blake3()
    raise ValueError(f"Unsupported algorithm: {algo}")


# ---------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------
def digest(
    data: Union[str, bytes],
    /,
    *,
    algo: Literal["sha256", "sha3_256", "blake2b", "blake3"] = "sha256",
    hex_output: bool = True,
) -> str | bytes:
    hasher = _new_hasher(Algo(algo))
    hasher.update(data.encode() if isinstance(data, str) else data)
    return hasher.hexdigest() if hex_output else hasher.digest()


def file_digest(
    file_path: Union[str, Path],
    /,
    *,
    algo: Literal["sha256", "sha3_256", "blake2b", "blake3"] = "sha256",
    hex_output: bool = True,
    chunk: int = 8192,
) -> str | bytes:
    hasher = _new_hasher(Algo(algo))
    with open(file_path, "rb") as f:
        while blk := f.read(chunk):
            hasher.update(blk)
    return hasher.hexdigest() if hex_output else hasher.digest()


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Hashing utility for cyber‑dojo.")
    p.add_argument("mode", choices=["string", "file"], help="string 或 file")
    p.add_argument("target", help="要雜湊的字串或檔案路徑")
    p.add_argument("--algo", choices=Algo.list(), default="sha256", help="雜湊演算法")
    p.add_argument(
        "--bytes",
        action="store_true",
        help="輸出 raw bytes（二進位）；預設輸出十六進位字串",
    )
    return p


def _cli(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    hex_out = not args.bytes

    try:
        if args.mode == "string":
            print(digest(args.target, algo=args.algo, hex_output=hex_out))
        else:
            path = Path(args.target)
            if not path.is_file():
                sys.exit(f"Error: {path} is not a file.")
            print(file_digest(path, algo=args.algo, hex_output=hex_out))
    except Exception as exc:  # pylint: disable=broad-except
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    _cli()
    # test example:
    # python src/hashing.py file   ./README.md --algo blake2b
    # python src/hashing.py string "hello" --algo sha256