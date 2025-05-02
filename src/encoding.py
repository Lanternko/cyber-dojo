# encoding.py – 基礎編碼/解碼工具
"""cyber‑dojo 專案的編碼/解碼輔助模組。

支援的 scheme：
- base64   : 標準 Base64 編碼（RFC 4648）
- base64url: URL‑safe Base64（去除 "=" padding 可選）
- hex      : 十六進位字串（大小寫皆可）
- url      : URL percent‑encoding（RFC 3986）

用法（CLI）：
    python encoding.py encode  base64 "hello world"
    python encoding.py decode  hex    "68656c6c6f"

此模組亦可被其他程式以 import 方式呼叫。
"""
from __future__ import annotations

import argparse
import base64
import binascii
import sys
import urllib.parse
from enum import Enum
from typing import Literal, Union

class Scheme(str, Enum):
    """編碼方案列舉類別"""
    BASE64 = "base64"
    BASE64URL = "base64url"
    HEX = "hex"
    URL = "url"

    @classmethod
    def list(cls) -> list[str]:
        """列出所有支援的編碼方案"""
        return [scheme.value for scheme in cls]
    
#----------------------------------------------------------------------
# Core Helper Functions
#----------------------------------------------------------------------

def _to_bytes(data: Union[str, bytes]) -> bytes:
    """將字串轉換為 bytes"""
    if isinstance(data, bytes):
        return data
    return data.encode()

def _to_str(data: Union[str, bytes]) -> str:
    """將 bytes 轉換為字串"""
    if isinstance(data, bytes):
        return data.decode()
    return data

#----------------------------------------------------------------------
# Public API
#----------------------------------------------------------------------

def encode(data: Union[str, bytes], scheme: Literal["base64", "base64url", "hex", "url"]) -> str:
    """將 *data* 依指定 *scheme* 轉為字串。
    Raises
    ------
    ValueError : 若 scheme 不被支援。
    """

    scheme_enum = Scheme(scheme)
    raw = _to_bytes(data)

    if scheme_enum == Scheme.BASE64:
        return base64.b64encode(raw).decode()
    if scheme_enum == Scheme.BASE64URL:
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")
    if scheme_enum == Scheme.HEX:
        return binascii.hexlify(raw).decode()
    if scheme_enum == Scheme.URL:
        return urllib.parse.quote_from_bytes(raw, safe="")
    
    raise ValueError(f"Unsupported scheme: {scheme}")

def decode(text: Union[str, bytes], scheme: Literal["base64", "base64url", "hex", "url"]) -> bytes:
    """將 *text* 依指定 *scheme* 還原為 bytes。
    Raises
    ------
    binascii.Error, ValueError : 若輸入格式不正確。"""

    scheme_enum = Scheme(scheme)
    s = _to_str(text) 

    if scheme_enum == Scheme.BASE64:   
        return base64.b64decode(s, validate=True)
    if scheme_enum == Scheme.BASE64URL: 
        # pad 補齊至 4 的倍數
        padding = "=" * (-len(s) % 4)
        return base64.urlsafe_b64decode(s + padding)
    if scheme_enum == Scheme.HEX:
        return binascii.unhexlify(s)
    if scheme_enum == Scheme.URL:
        return urllib.parse.unquote_to_bytes(s)
    
    raise ValueError(f"Unsupported scheme: {scheme}")

#----------------------------------------------------------------------
# Command Line Interface
#----------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    """建立命令列解析器"""
    p = argparse.ArgumentParser(description="Encoding/Decoding Tool for cyber‑dojo.")
    sub = p.add_subparsers(dest="command", required=True)

    # encode sub-command
    e = sub.add_parser("encode", help="Enode data with given scheme.")
    e.add_argument("scheme", choices=Scheme.list())
    e.add_argument("data", help="Raw string to encode.")

    # decode sub-command
    d = sub.add_parser("decode", help="Decode text with given scheme.")
    d.add_argument("scheme", choices=Scheme.list())
    d.add_argument("text", help="Text to decode.")
    d.add_argument("--to-str", action="store_true", help="Output as UTF-8 string instead of bytes.")

    return p

def _cli(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)     

    try:
        if args.command == "encode":
            out = encode(args.data, args.scheme)
            print(out)
        elif args.command == "decode":
            out = decode(args.text, args.scheme)
            print(out.decode() if args.to_str else out)
            
    except Exception as exc:    #pylint: disable=broad-except
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)

if __name__ == "__main__":  # pragma: no cover
    _cli()
    
