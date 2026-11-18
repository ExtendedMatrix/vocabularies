"""The vocabulary PACKAGES (MICRO-U, E.D. 18 Nov 2026): every card says what an
EM tool must show and obey — licence, tier, attribution — and a package carries
its source UNMODIFIED. Tier C is never built."""
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import build_packages  # noqa: E402

CARDS = {p.parent.name: yaml.safe_load(p.read_text(encoding="utf-8"))
         for p in sorted((REPO / "packages").glob("*/package.yaml"))}
ICCD = Path(os.environ.get("STRATIGRAPH_ICCD_STANDARDS",
                           Path.home() / "Documents/GitHub/Standard-catalografici"))


def test_there_are_packages():
    assert {"iccd-ra-materia", "getty-aat-materials"} <= set(CARDS)


@pytest.mark.parametrize("pid", sorted(CARDS))
def test_every_card_says_licence_tier_attribution(pid):
    c = CARDS[pid]
    assert c["id"] == pid
    assert c["tier"] in {"A", "B", "C"}
    for k in ("license", "attribution", "title", "serves", "source"):
        assert c.get(k), f"{pid}: {k} missing"
    if c["tier"] == "B":
        assert "SA" in c["license"].upper(), f"{pid}: tier B is the share-alike tier"
    if c["source"]["from"] == "iccd_standards":
        assert c["tier"] == "B"


@pytest.mark.skipif(not ICCD.is_dir(), reason="no Standard-catalografici checkout")
def test_the_iccd_package_carries_the_file_unmodified(tmp_path):
    build_packages.main([str(tmp_path), "iccd-ra-materia", "--iccd", str(ICCD)])
    cat = json.loads((tmp_path / "catalog.json").read_text())
    (pkg,) = cat["packages"]
    z = zipfile.ZipFile(tmp_path / pkg["url"])
    m = json.loads(z.read("manifest.json"))
    data = z.read(m["source"]["file"])
    original = (ICCD / CARDS["iccd-ra-materia"]["source"]["path"]).read_bytes()
    assert data == original
    assert m["source"]["sha256"] == hashlib.sha256(original).hexdigest()
    assert m["format"] == "em-vocabulary-package/1" and m["tier"] == "B"
    assert "index.json" not in z.namelist()          # the index is compiled on the machine
    # the same input gives the same bytes
    build_packages.main([str(tmp_path / "again"), "iccd-ra-materia", "--iccd", str(ICCD)])
    assert (tmp_path / "again" / pkg["url"]).read_bytes() == (tmp_path / pkg["url"]).read_bytes()


def test_an_export_package_is_dated_by_its_export(tmp_path):
    nt = tmp_path / "x.nt"
    nt.write_text('<http://vocab.getty.edu/aat/300011286> '
                  '<http://www.w3.org/2004/02/skos/core#prefLabel> "limestone"@en .\n')
    build_packages.main([str(tmp_path / "d"), "getty-aat-materials",
                         "--export", f"getty-aat-materials={nt}", "--date", "2026-11-18"])
    (pkg,) = json.loads((tmp_path / "d" / "catalog.json").read_text())["packages"]
    assert pkg["version"] == pkg["snapshot_date"] == "2026-11-18"
    assert pkg["languages"] == ["en"] and pkg["tier"] == "A"
