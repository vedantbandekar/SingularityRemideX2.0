"""
AI Helper module for RemideX
Handles medicine search using CSV dataset
Falls back to AI agent when dataset is insufficient
"""

from utils.ai_client import ask_ai_agent
import pandas as pd
import os
import json
from typing import List, Dict, Optional
from rapidfuzz import fuzz, process

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'data',
    'cleaned_medicine_data.csv'
)


class MedicineSearch:
    def __init__(self):
        self.df = None
        self._load_data()

    def _load_data(self):
        try:
            self.df = pd.read_csv(CSV_PATH)
            self.df.columns = self.df.columns.str.strip().str.lower()
        except Exception as e:
            print(f"Error loading medicine data: {e}")
            self.df = pd.DataFrame()

    # ---------------- SAFETY CHECKS ---------------- #

    def _is_small_talk(self, query: str) -> bool:
        greetings = [
            "hi", "hello", "hey", "thanks", "thank you",
            "who are you", "what is your name", "help"
        ]
        return any(greet in query.lower() for greet in greetings)

    def _has_medicine_intent(self, query: str) -> bool:
        keywords = [
            "medicine", "tablet", "drug", "price",
            "side effect", "dosage", "use", "composition",
            "salt", "interaction"
        ]
        return any(word in query.lower() for word in keywords)

    # ---------------- SEARCH LOGIC ---------------- #

    def search_medicine(self, query: str, limit: int = 5) -> List[Dict]:
        if self.df.empty or not query:
            return []

        medicine_names = self.df['name'].tolist()

        matches = process.extract(
            query.lower(),
            [name.lower() for name in medicine_names],
            scorer=fuzz.WRatio,
            limit=limit
        )

        results = []
        for match_name, score, _ in matches:
            if score >= 85:  # IMPORTANT FIX
                row = self.df[self.df['name'].str.lower() == match_name].iloc[0]
                results.append(self._format_medicine_info(row, score))

        return results

    def _format_medicine_info(self, row: pd.Series, match_score: int = 100) -> Dict:
        interactions = self._parse_interactions(row.get('drug_interactions', '{}'))

        return {
            "name": row.get("name", "N/A"),
            "price": row.get("price", "N/A"),
            "manufacturer": row.get("manufacturer_name", "N/A"),
            "pack_size": row.get("pack_size_label", "N/A"),
            "salt_composition": row.get("salt_composition", "N/A"),
            "description": row.get("medicine_desc", "No description available"),
            "side_effects": row.get("side_effects", "No side effects listed"),
            "drug_interactions": interactions,
            "is_discontinued": row.get("is_discontinued", False),
            "match_score": match_score
        }

    def _parse_interactions(self, interactions_str: str) -> Dict:
        try:
            if pd.isna(interactions_str) or not interactions_str:
                return {"drug": [], "brand": [], "effect": []}
            interactions_str = interactions_str.replace('""', '"')
            return json.loads(interactions_str)
        except Exception:
            return {"drug": [], "brand": [], "effect": []}

    # ---------------- DATASET ANSWER ---------------- #

    def _dataset_based_answer(self, query: str) -> Optional[str]:
        if self._is_small_talk(query):
            return None

        if not self._has_medicine_intent(query):
            return None

        results = self.search_medicine(query, limit=3)

        if not results:
            return None

        response = []

        for med in results:
            response.append(f"### 💊 {med['name']}")
            response.append(f"**Manufacturer:** {med['manufacturer']}")
            response.append(f"**Price:** ₹{med['price']}")
            response.append(f"**Pack Size:** {med['pack_size']}")
            response.append(f"**Composition:** {med['salt_composition']}")
            response.append(f"**Side Effects:** {med['side_effects']}")
            response.append("---")

        return "\n".join(response)

    # ---------------- MAIN ENTRY ---------------- #

    def answer_query(self, query: str) -> str:
        dataset_response = self._dataset_based_answer(query)

        if dataset_response:
            return dataset_response

        return ask_ai_agent(
            message=query,
            user_id="remidex_user",
            session_id="remidex_session"
        )


# ---------------- SINGLETON ---------------- #

_medicine_search = None


def get_medicine_search() -> MedicineSearch:
    global _medicine_search
    if _medicine_search is None:
        _medicine_search = MedicineSearch()
    return _medicine_search
