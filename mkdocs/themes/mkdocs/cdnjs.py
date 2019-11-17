#!/usr/bin/env python3
# Copyright 2019 Nicolas Braud-Santoni <nicoo@debian.org>

import base64
import json
from pathlib import Path

import requests


def hash_url(url, hash_alg="sha384"):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes

    if hash_alg not in ["sha384"]:
        raise ValueError(f"Invalid hash algorithm: '{hash_alg}'")

    digest = hashes.Hash(hashes.SHA384(), backend=default_backend())
    response = requests.get(url)
    response.raise_for_status()
    digest.update(response.content)

    return f"{hash_alg}-{base64.b64encode(digest.finalize()).decode('ascii')}"


def cdnjs_lib(lib, version=None):
    metadata = requests.get(f"https://api.cdnjs.com/libraries/{lib}").json()
    assets = {release["version"]: release["files"] for release in metadata["assets"]}

    if version in [None, "latest"]:
        from distutils.version import LooseVersion

        version = max(assets, key=LooseVersion)

    return [f"{asset}" for asset in assets[version]]


def cdnjs_url(library, version, file):
    return f"https://cdnjs.cloudflare.com/ajax/libs/{library}/{version}/{file}"


if __name__ == "__main__":
    with (Path(__file__).parent / "cdnjs_libraries.json").open() as libs_f:
        libs = json.load(libs_f)

    result = {}
    for lib, version in libs.items():
        result[lib] = {}
        result[lib][version] = {}
        for asset in cdnjs_lib(lib, version):
            result[lib][version][asset] = hash_url(cdnjs_url(lib, version, asset))

    with (Path(__file__).parent / "cdnjs_hashes.j2").open("w") as result_f:
        result_f.write("{%- set cdnjs_hashes = ")
        json.dump(result, result_f, indent=2)
        result_f.write(" -%}")
