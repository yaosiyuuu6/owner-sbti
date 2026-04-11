#!/usr/bin/env python3
"""Serve a generated report HTML file over localhost and print a clickable URL."""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver
import sys
from pathlib import Path
from urllib.parse import quote


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="Path to the generated HTML report.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind. Defaults to 8765.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    file_path = Path(args.file).expanduser().resolve()
    if not file_path.exists():
        raise SystemExit(f"Report not found: {file_path}")
    if file_path.suffix.lower() != ".html":
        raise SystemExit("Expected an .html file")

    directory = file_path.parent
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer((args.host, args.port), handler) as httpd:
        rel_name = quote(file_path.name)
        url = f"http://{args.host}:{args.port}/{rel_name}"
        print(url, flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
