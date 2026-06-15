import os
import json
import string
from pathlib import Path
from collections import Counter

import numpy as np
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from chromadb.config import Settings

CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma"
COLLECTION_NAME = "plant_knowledge"

_client = None
_collection = None


class TfIdfEmbeddingFunction(EmbeddingFunction):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_vocab"):
            self._vocab: dict[str, int] = {}
            self._idf: dict[str, float] = {}
            self._dim = 512
            self._fitted = False

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower().translate(str.maketrans("", "", string.punctuation))
        return [w for w in text.split() if len(w) > 2]

    def _ngrams(self, tokens: list[str]) -> list[str]:
        result = []
        for t in tokens:
            for i in range(len(t) - 1):
                result.append(t[i:i + 2])
        return result

    def _text_to_vector(self, text: str) -> np.ndarray:
        tokens = self._tokenize(text)
        grams = self._ngrams(tokens)
        counts = Counter(grams)
        vec = np.zeros(self._dim, dtype=np.float32)
        for gram, count in counts.items():
            idx = abs(hash(gram)) % self._dim
            weight = count * self._idf.get(gram, 1.0)
            vec[idx] = weight
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def fit(self, docs: list[str]):
        tokens = []
        for doc in docs:
            tokens.extend(self._ngrams(self._tokenize(doc)))
        total = len(tokens)
        counter = Counter(tokens)
        self._idf = {g: np.log(1 + total / (1 + c)) for g, c in counter.items()}
        self._fitted = True

    def __call__(self, input: Documents) -> Embeddings:
        if not self._fitted:
            self.fit(input)
        return [self._text_to_vector(d).tolist() for d in input]


def _get_embedding_function():
    return TfIdfEmbeddingFunction()


def _get_client():
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = _get_client()
        ef = _get_embedding_function()
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME in existing:
            _collection = client.get_collection(COLLECTION_NAME, embedding_function=ef)
        else:
            _collection = client.create_collection(COLLECTION_NAME, embedding_function=ef)
    return _collection


def query_knowledge(query: str, n_results: int = 5) -> list[dict]:
    col = get_collection()
    results = col.query(query_texts=[query], n_results=n_results)
    docs = []
    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = (results["metadatas"][0] or [{}])[i] if results.get("metadatas") else {}
            docs.append({"content": doc, "metadata": meta})
    return docs


def add_document(text: str, metadata: dict | None = None, doc_id: str | None = None):
    col = get_collection()
    col.add(documents=[text], metadatas=[metadata or {}], ids=[doc_id or str(hash(text))])


def add_documents(docs: list[dict]):
    col = get_collection()
    texts = [d["text"] for d in docs]
    metadatas = [d.get("metadata", {}) for d in docs]
    ids = [d.get("id", str(hash(d["text"]))) for d in docs]
    col.add(documents=texts, metadatas=metadatas, ids=ids)


def count_documents() -> int:
    col = get_collection()
    try:
        return col.count()
    except Exception:
        return 0


def seed_knowledge_base():
    try:
        if count_documents() > 0:
            return
    except Exception:
        pass

    docs = [
        {
            "text": (
                "OEE (Overall Equipment Effectiveness) is calculated as: "
                "Availability × Performance × Quality. "
                "Availability = Run Time / Planned Production Time. "
                "Performance = (Ideal Cycle Time × Total Parts) / Run Time. "
                "Quality = Good Parts / Total Parts. "
                "Target OEE: >85% (world-class), >75% (good), >60% (typical)."
            ),
            "metadata": {"category": "oee", "source": "industry_standard"},
        },
        {
            "text": (
                "LINE-01 (Assembly Line 1): High-speed automated assembly line. "
                "Handles final product assembly. Typical cycle time: 40-45 sec. "
                "Common faults: sensor misalignment, solder joint defects, conveyor jams."
            ),
            "metadata": {"category": "machine_profile", "machine_id": "LINE-01"},
        },
        {
            "text": (
                "LINE-02 (Assembly Line 2): Medium-speed assembly line for sub-components. "
                "Typical cycle time: 42-48 sec. "
                "Common faults: feeder mechanism jams, pneumatic pressure drops, vision system errors."
            ),
            "metadata": {"category": "machine_profile", "machine_id": "LINE-02"},
        },
        {
            "text": (
                "LINE-03 (Assembly Line 3): Older assembly line, scheduled for upgrade. "
                "Typical cycle time: 50-60 sec. "
                "Common faults: motor overheating, belt slippage, bearing wear, electrical noise."
                "This line requires more frequent preventive maintenance."
            ),
            "metadata": {"category": "machine_profile", "machine_id": "LINE-03"},
        },
        {
            "text": (
                "LINE-04 (Packaging Line): Automated packaging and palletizing line. "
                "Typical cycle time: 35-40 sec. "
                "Common faults: film wrapper jams, labeler misalignment, palletizer sensor faults."
                "Highest OEE in the plant — well-maintained and reliable."
            ),
            "metadata": {"category": "machine_profile", "machine_id": "LINE-04"},
        },
        {
            "text": (
                "LINE-05 (Quality Testing Line): Automated inspection and testing line. "
                "Typical cycle time: 38-44 sec. "
                "Common faults: camera calibration drift, conveyor speed variation, reject mechanism jams."
            ),
            "metadata": {"category": "machine_profile", "machine_id": "LINE-05"},
        },
        {
            "text": (
                "Troubleshooting: Conveyor belt motor over temperature. "
                "Symptoms: Motor housing hot to touch, thermal cutoff trips repeatedly. "
                "Root causes: (1) Bearing failure — check for grinding noise, (2) Belt tension too high, "
                "(3) Motor cooling fan blocked, (4) Electrical overload. "
                "Resolution: Inspect bearings, check belt tension with tension gauge, "
                "clean cooling fan intake, measure current draw with clamp meter."
            ),
            "metadata": {"category": "troubleshooting", "machine_id": "LINE-03", "fault": "motor_over_temp"},
        },
        {
            "text": (
                "Troubleshooting: Pneumatic pressure drops on assembly line. "
                "Symptoms: Actuators move slowly or stall, pressure gauge shows <80 PSI. "
                "Root causes: (1) Compressor not cycling, (2) Leak in airline, "
                "(3) Clogged air filter, (4) Pressure regulator failure. "
                "Resolution: Check compressor operation, listen for air leaks, "
                "replace air filter element, verify regulator setting at 90 PSI."
            ),
            "metadata": {"category": "troubleshooting", "machine_id": "LINE-02", "fault": "pneumatic_pressure"},
        },
        {
            "text": (
                "Troubleshooting: Vision system inspection errors. "
                "Symptoms: High false reject rate, system unable to locate inspection features. "
                "Root causes: (1) Camera lens dirty, (2) Lighting change or LED failure, "
                "(3) Part positioning variation, (4) Calibration drift. "
                "Resolution: Clean lens with lint-free cloth, check all LED array elements, "
                "run calibration routine, adjust part nest guides if worn."
            ),
            "metadata": {"category": "troubleshooting", "machine_id": "LINE-05", "fault": "vision_error"},
        },
        {
            "text": (
                "Troubleshooting: Solder joint quality defects. "
                "Symptoms: Cold solder joints, solder balls, insufficient wetting. "
                "Root causes: (1) Reflow temperature profile incorrect, "
                "(2) Solder paste expired or improperly stored, "
                "(3) PCB contamination, (4) Nitrogen flow too low. "
                "Resolution: Verify reflow oven profile against solder spec, "
                "check paste use-by date, verify PCB cleaning process, "
                "adjust nitrogen flow to 15-20 L/min."
            ),
            "metadata": {"category": "troubleshooting", "machine_id": "LINE-01", "fault": "solder_defects"},
        },
        {
            "text": (
                "Preventive Maintenance Schedule:\n"
                "Daily: Visual inspection, clean sensors, check fluid levels.\n"
                "Weekly: Lubricate bearings, check belt tension, verify safety systems.\n"
                "Monthly: Inspect/replace air filters, check electrical connections, "
                "calibrate sensors.\n"
                "Quarterly: Replace wear parts (belts, bearings, seals), "
                "check motor insulation resistance, verify emergency stops.\n"
                "Annually: Major overhaul, replace motors if vibration > 7 mm/s, "
                "recalibrate all instruments, update control software."
            ),
            "metadata": {"category": "maintenance", "source": "plant_standard"},
        },
        {
            "text": (
                "Alarm Severity Guidelines:\n"
                "CRITICAL: Immediate shutdown risk or safety hazard. "
                "Respond within 5 minutes. Notify shift supervisor.\n"
                "WARNING: Potential issue developing. Respond within 1 hour. "
                "Log in shift report.\n"
                "INFO: Normal operational notification. Respond within 24 hours. "
                "Document in maintenance log."
            ),
            "metadata": {"category": "procedures", "source": "alarm_policy"},
        },
        {
            "text": (
                "Root Cause Analysis (RCA) Process:\n"
                "1. Define the problem clearly with measurable impact.\n"
                "2. Collect data — machine logs, alarm history, maintenance records.\n"
                "3. Identify causal factors using 5 Whys technique.\n"
                "4. Identify root cause(s) — distinguish physical, human, and latent causes.\n"
                "5. Implement corrective actions with owners and deadlines.\n"
                "6. Verify effectiveness — monitor KPIs for 30 days.\n"
                "7. Standardize — update procedures, training, and preventive maintenance."
            ),
            "metadata": {"category": "procedures", "source": "quality_system"},
        },
        {
            "text": (
                "Energy efficiency guidelines:\n"
                "- Motors should be turned off when lines are idle for >15 minutes.\n"
                "- LED lighting replacement reduces energy use by 60%.\n"
                "- Compressed air leaks cost approximately $0.25/CFM annually.\n"
                "- Variable frequency drives reduce motor energy consumption by 20-40%.\n"
                "- Preventive maintenance improves energy efficiency by 5-15%."
            ),
            "metadata": {"category": "guidelines", "source": "energy_management"},
        },
    ]

    add_documents(docs)
    print(f"Seeded {len(docs)} documents into ChromaDB knowledge base")
