#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Load the local PNG asset library used by the HTML renderer."""

import json
import os
from pathlib import Path


def default_manifest_path(skill_dir: str) -> str:
    """The planned layout puts manifest/ next to xuan-docx-to-wechat-html/."""
    return str(Path(skill_dir).resolve().parent / "manifest" / "manifest.json")


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def _normalize_asset(asset: dict, manifest_dir: Path) -> dict | None:
    file_name = asset.get("file") or asset.get("suggested_file")
    if not file_name:
        return None

    asset_path = Path(file_name)
    if not asset_path.is_absolute():
        asset_path = manifest_dir / asset_path
    exists = asset_path.exists()

    status = asset.get("status", "")
    # If the PNG file exists, treat it as usable even if the placeholder status
    # was not updated yet. This keeps the library easy to maintain by hand.
    if status == "pending_png" and not exists:
        return None

    item = dict(asset)
    item["path"] = str(asset_path)
    item["exists"] = exists
    item["file"] = file_name
    return item


def _collect_assets(manifest: dict, manifest_dir: Path) -> list:
    collected = []
    for section_name in ("assets", "asset_slots"):
        for asset in manifest.get(section_name, []) or []:
            normalized = _normalize_asset(asset, manifest_dir)
            if normalized:
                collected.append(normalized)
    return collected


def load_asset_library(manifest_path: str, article_type: str) -> dict:
    """Load common assets plus the assets for the detected article type.

    Missing manifests are not fatal. The renderer will simply skip PNG
    decorations and continue generating a compatible HTML article.
    """
    if not manifest_path:
        return {
            "manifest_path": "",
            "article_type": article_type,
            "available": False,
            "assets": [],
            "assets_by_id": {},
            "missing_reason": "manifest_path_empty",
        }

    root_path = Path(manifest_path).resolve()
    if not root_path.exists():
        return {
            "manifest_path": str(root_path),
            "article_type": article_type,
            "available": False,
            "assets": [],
            "assets_by_id": {},
            "missing_reason": "root_manifest_not_found",
        }

    root_manifest = _read_json(root_path)
    base_path = Path(root_manifest.get("base_path") or root_path.parent).resolve()
    if not base_path.exists():
        base_path = root_path.parent

    manifest_refs = []
    common_ref = root_manifest.get("common_manifest")
    if common_ref:
        manifest_refs.append(("common", common_ref))

    type_ref = (root_manifest.get("article_type_manifests") or {}).get(article_type)
    if type_ref:
        manifest_refs.append((article_type, type_ref))

    assets = []
    loaded_manifests = []
    for manifest_type, rel_path in manifest_refs:
        child_path = Path(rel_path)
        if not child_path.is_absolute():
            child_path = base_path / child_path
        if not child_path.exists():
            continue
        child_manifest = _read_json(child_path)
        loaded_manifests.append(str(child_path))
        for asset in _collect_assets(child_manifest, child_path.parent):
            asset["manifest_type"] = manifest_type
            assets.append(asset)

    assets_by_id = {}
    for asset in assets:
        asset_id = asset.get("id")
        if asset_id and asset_id not in assets_by_id:
            assets_by_id[asset_id] = asset

    return {
        "manifest_path": str(root_path),
        "base_path": str(base_path),
        "article_type": article_type,
        "available": True,
        "loaded_manifests": loaded_manifests,
        "assets": assets,
        "assets_by_id": assets_by_id,
        "missing_reason": "",
    }


def public_asset_summary(asset_library: dict) -> dict:
    """Return JSON-safe information for stdout/debug output."""
    return {
        "manifest_path": asset_library.get("manifest_path", ""),
        "base_path": asset_library.get("base_path", ""),
        "article_type": asset_library.get("article_type", ""),
        "available": bool(asset_library.get("available")),
        "loaded_manifests": asset_library.get("loaded_manifests", []),
        "missing_reason": asset_library.get("missing_reason", ""),
        "used_assets": [
            {
                "id": asset.get("id", ""),
                "path": asset.get("path", ""),
                "use_for": asset.get("use_for", ""),
                "placement": asset.get("placement", ""),
                "manifest_type": asset.get("manifest_type", ""),
            }
            for asset in asset_library.get("used_assets", []) or []
        ],
    }
