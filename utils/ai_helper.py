"""
AI Helper module for RemideX
Hybrid system:
- Uses CSV for medicine-specific queries
- Uses AI agent for general / conversational queries
"""

from utils.ai_client import ask_ai_agent

import pandas as pd
import os
import json
from typing import List, Dict, Optional
from rapidfuzz import fuzz, process

# ---------------- PATH ---------------- #

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "cleaned_medicine_data.csv"
)

# ---------------- INTENT KEYWORDS ---------------- #

MEDICAL_KEYWORDS = [
    "medicine", "drug", "tablet", "capsule",
    "side effect", "effects", "reaction",
    "ingredient", "composition", "salt",
    "dosage", "dose", "price", "use", "uses",
    "interaction", "combine"
]

CASUAL_KEYWORDS = [
    "hello", "hi", "hey", "thanks",
    "thank you", "help", "who are you",
    "what can you do"
]


class MedicineSearch:
    """Hybrid medicine + AI query handler"""

    def __init__(self):
        self.df = None
        self._load_data()

    def _load_data(self):
        try:
            self.df = pd.read_csv(CSV_PATH)
            self.df.columns = self.df.columns.str.strip().str.lower()
        except Exception as e:
            print(f"CSV load error: {e}")
            self.df = pd.DataFrame()

    # ---------------- UTILS ---------------- #

    def _is_casual_query(self, query: str) -> bool:
        q = query.lower()
        return any(word in q for word in CASUAL_KEYWORDS)

    def _is_medical_query(self, query: str) -> bool:
        q = query.lower()
        return any(word in q for word in MEDICAL_KEYWORDS)

    # ---------------- SEARCH ---------------- #

    def search_medicine(self, query: str, limit: int = 3) -> List[Dict]:
        if self.df.empty or not query:
            return []

        names = self.df["name"].tolist()

        matches = process.extract(
            query.lower(),
            [n.lower() for n in names],
            scorer=fuzz.WRatio,
            limit=limit
        )

        results = []
        for match_name, score, _ in matches:
            if score >= 70:  # 🔥 IMPORTANT THRESHOLD
                row = self.df[self.df["name"].str.lower() == match_name].iloc[0]
                results.append(self._format_medicine(row, score))

        return results

    def _format_medicine(self, row: pd.Series, score: int) -> Dict:
        return {
            "name": row.get("name", "N/A"),
            "manufacturer": row.get("manufacturer_name", "N/A"),
            "price": row.get("price", "N/A"),
            "pack_size": row.get("pack_size_label", "N/A"),
            "salt_composition": row.get("salt_composition", "N/A"),
            "description": row.get("medicine_desc", "No description available"),
            "side_effects": row.get("side_effects", "No side effects listed"),
            "match_score": score
        }

    # ---------------- ANSWER ENGINE ---------------- #

    def answer_query(self, query: str) -> str:
        """
        Decision flow:
        1. Casual → AI
        2. Medical → CSV
        3. CSV fails → AI
        """

        # 1️⃣ Casual conversation → AI
        if self._is_casual_query(query):
            return ask_ai_agent(
                message=query,
                user_id="remidex_user",
                session_id="remidex_session"
            )

        # 2️⃣ Medical intent → CSV
        if self._is_medical_query(query):
            results = self.search_medicine(query)

            if results:
                return self._format_csv_response(results, query)

        # 3️⃣ Fallback → AI
        return ask_ai_agent(
            message=query,
            user_id="remidex_user",
            session_id="remidex_session"
        )

    # ---------------- FORMAT CSV RESPONSE ---------------- #

    def _format_csv_response(self, meds: List[Dict], query: str) -> str:
        q = query.lower()
        output = []

        for med in meds:
            output.append(f"💊 {med['name']}")
            output.append(f"Manufacturer: {med['manufacturer']}")
            output.append(f"Price: ₹{med['price']}")
            output.append(f"Pack Size: {med['pack_size']}\n")

            if "ingredient" in q or "composition" in q:
                output.append(f"Composition: {med['salt_composition']}\n")

            if "side" in q or "effect" in q:
                output.append(f"Side Effects: {med['side_effects']}\n")

            if "use" in q or "about" in q:
                output.append(f"Description: {med['description'][:500]}...\n")

            output.append("-" * 30)

        return "\n".join(output)

    def get_all_medicine_names(self) -> List[str]:
        if self.df.empty:
            return []
        return sorted(self.df["name"].tolist())


# ---------------- SINGLETON ---------------- #

_medicine_search = None


def get_medicine_search() -> MedicineSearch:
    global _medicine_search
    if _medicine_search is None:
        _medicine_search = MedicineSearch()
    return _medicine_search
