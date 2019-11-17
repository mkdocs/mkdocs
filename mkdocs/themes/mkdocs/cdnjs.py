#!/usr/bin/env python3
# Copyright 2019 Nicolas Braud-Santoni <nicoo@debian.org>

import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes
import requests


hash_algs = {
    'sha256': hashes.SHA256,
    'sha384': hashes.SHA384,
    'sha512': hashes.SHA512,
}


def hash_url(url, hash_alg="sha384"):
    from cryptography.hazmat.backends import default_backend

    try:
        hasher = hash_algs[hash_alg]()
    except KeyError:
        raise ValueError(f"Invalid hash algorithm: '{hash_alg}'")

    digest = hashes.Hash(hasher, backend=default_backend())
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

    return version, [f"{asset}" for asset in assets[version]]


def cdnjs_url(library, version, file):
    return f"https://cdnjs.cloudflare.com/ajax/libs/{library}/{version}/{file}"


if __name__ == "__main__":
    with (Path(__file__).parent / "cdnjs_libraries.json").open() as libs_f:
        libs = json.load(libs_f)

    result = {}
    for lib, v in libs.items():
        result[lib] = {}
        version, assets = cdnjs_lib(lib, v)
        print(f"Fetching and hashing {len(assets)} assets for '{lib}' version '{version}'")

        result[lib]['version'] = version
        result[lib]['assets'] = {}
        for asset in assets:
            result[lib]['assets'][asset] = hash_url(cdnjs_url(lib, version, asset))

    with (Path(__file__).parent / "cdnjs_hashes.j2").open("w") as result_f:
        result_f.write("{%- set cdnjs_hashes = ")
        json.dump(result, result_f, indent=2)
        result_f.write(" -%}\n")
