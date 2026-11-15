"""Offline resource checks. Does not validate Azure connectivity or execute pipelines."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"DatasetReference": "dataset", "LinkedServiceReference": "linkedService", "PipelineReference": "pipeline", "DataFlowReference": "dataflow", "IntegrationRuntimeReference": "integrationRuntime"}

def check(value):
    if isinstance(value, dict):
        kind, name = value.get("type"), value.get("referenceName")
        if kind in KINDS and isinstance(name, str) and not name.startswith("@"):
            assert name == "AutoResolveIntegrationRuntime" or (ROOT / KINDS[kind] / (name + ".json")).is_file(), f"Missing {kind}: {name}"
        assert "encryptedCredential" not in value, "Replace factory-bound credentials with managed identity or Key Vault"
        if value.get("type") == "Copy":
            inputs = {x["referenceName"] for x in value.get("inputs", [])}
            outputs = {x["referenceName"] for x in value.get("outputs", [])}
            assert not inputs & outputs, "Copy reads and writes the same dataset"
            source = value.get("typeProperties", {}).get("source", {}).get("storeSettings", {}).get("type")
            for item in value.get("inputs", []):
                dataset = json.loads((ROOT / "dataset" / (item["referenceName"] + ".json")).read_text())
                location = dataset["properties"].get("typeProperties", {}).get("location", {}).get("type")
                expected = {"HttpServerLocation": "HttpReadSettings", "AzureBlobFSLocation": "AzureBlobFSReadSettings", "AzureBlobStorageLocation": "AzureBlobStorageReadSettings"}.get(location)
                if expected:
                    assert source == expected, f"{value.get('name')}: source settings disagree with {location}"
        for child in value.values():
            check(child)
    elif isinstance(value, list):
        for child in value:
            check(child)

count = 0
for folder in ["factory", "dataset", "linkedService", "pipeline"]:
    for path in (ROOT / folder).glob("*.json"):
        document = json.loads(path.read_text())
        assert document["name"] == path.stem, f"Resource name mismatch: {path}"
        check(document)
        if folder == "pipeline":
            activities = {a["name"]: a for a in document["properties"]["activities"]}
            for activity in activities.values():
                if activity["type"] == "ForEach":
                    expression = activity["typeProperties"]["items"].get("value", "")
                    for name, lookup in activities.items():
                        if lookup["type"] == "Lookup" and f"activity('{name}').output.value" in expression:
                            assert lookup["typeProperties"].get("firstRowOnly") is False, f"{name} must return an array for ForEach"
        count += 1
for path in ROOT.glob("*.ipynb"):
    notebook = json.loads(path.read_text())
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            compile("".join(cell["source"]), f"{path.name}:cell{index}", "exec")
print(f"PASS: {count} ADF resources; references, copy source settings and notebook syntax checked")
