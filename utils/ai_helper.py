"""
AI Helper module for Remidex
Handles medicine search and AI-powered explanations
"""

import pandas as pd
import os
import json
from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz, process

# Path to medicine data CSV
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_medicine_data.csv')


class MedicineSearch:
    """Search and query medicine database with fuzzy matching"""
    
    def __init__(self):
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """Load the medicine CSV data"""
        try:
            self.df = pd.read_csv(CSV_PATH)
            # Clean column names
            self.df.columns = self.df.columns.str.strip().str.lower()
        except Exception as e:
            print(f"Error loading medicine data: {e}")
            self.df = pd.DataFrame()
    
    def search_medicine(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for medicines by name using fuzzy matching.
        Returns top matches with their details.
        """
        if self.df.empty or not query:
            return []
        
        # Get medicine names
        medicine_names = self.df['name'].tolist()
        
        # Fuzzy search
        matches = process.extract(
            query.lower(),
            [name.lower() for name in medicine_names],
            scorer=fuzz.WRatio,
            limit=limit
        )
        
        results = []
        for match_name, score, idx in matches:
            if score >= 50:  # Minimum threshold
                # Find the original row
                row = self.df[self.df['name'].str.lower() == match_name].iloc[0]
                results.append(self._format_medicine_info(row, score))
        
        return results
    
    def get_medicine_by_name(self, name: str) -> Optional[Dict]:
        """Get exact medicine details by name"""
        if self.df.empty:
            return None
        
        mask = self.df['name'].str.lower() == name.lower()
        if mask.any():
            row = self.df[mask].iloc[0]
            return self._format_medicine_info(row)
        return None
    
    def _format_medicine_info(self, row: pd.Series, match_score: int = 100) -> Dict:
        """Format medicine row into a dictionary"""
        # Parse drug interactions JSON
        interactions = self._parse_interactions(row.get('drug_interactions', '{}'))
        
        return {
            'name': row.get('name', 'N/A'),
            'price': row.get('price', 'N/A'),
            'manufacturer': row.get('manufacturer_name', 'N/A'),
            'pack_size': row.get('pack_size_label', 'N/A'),
            'salt_composition': row.get('salt_composition', 'N/A'),
            'description': row.get('medicine_desc', 'No description available'),
            'side_effects': row.get('side_effects', 'No side effects listed'),
            'drug_interactions': interactions,
            'is_discontinued': row.get('is_discontinued', False),
            'match_score': match_score
        }
    
    def _parse_interactions(self, interactions_str: str) -> Dict:
        """Parse drug interactions from JSON string"""
        try:
            if pd.isna(interactions_str) or not interactions_str:
                return {'drug': [], 'brand': [], 'effect': []}
            interactions_str = interactions_str.replace('""', '"')
            return json.loads(interactions_str)
        except (json.JSONDecodeError, TypeError):
            return {'drug': [], 'brand': [], 'effect': []}
    
    def get_medicine_suggestions(self, partial_name: str, limit: int = 10) -> List[str]:
        """Get medicine name suggestions for autocomplete"""
        if self.df.empty or not partial_name:
            return []
        
        mask = self.df['name'].str.lower().str.contains(partial_name.lower(), na=False)
        matches = self.df[mask]['name'].head(limit).tolist()
        return matches
    
    def answer_query(self, query: str) -> str:
        """
        Answer a natural language query about medicines.
        Returns a formatted response with relevant information.
        """
        query_lower = query.lower()
        
        # Try to find medicine name in query
        results = self.search_medicine(query, limit=3)
        
        if not results:
            return "I couldn't find any matching medicines. Please try searching with a different name or check the spelling."
        
        # Format response
        response_parts = []
        
        for med in results:
            response_parts.append(f"### 💊 {med['name']}")
            response_parts.append(f"**Manufacturer:** {med['manufacturer']}")
            response_parts.append(f"**Price:** ₹{med['price']}")
            response_parts.append(f"**Pack Size:** {med['pack_size']}")
            response_parts.append("")
            
            # Check what the user is asking about
            if any(word in query_lower for word in ['ingredient', 'composition', 'salt', 'contain']):
                response_parts.append(f"**🧪 Composition:** {med['salt_composition']}")
                response_parts.append("")
            
            if any(word in query_lower for word in ['side effect', 'effect', 'reaction', 'symptom']):
                response_parts.append(f"**⚠️ Side Effects:** {med['side_effects']}")
                response_parts.append("")
            
            if any(word in query_lower for word in ['interaction', 'interact', 'with other', 'combine']):
                interactions = med['drug_interactions']
                if interactions.get('drug'):
                    response_parts.append("**🔗 Drug Interactions:**")
                    for drug, effect in zip(interactions['drug'], interactions['effect']):
                        response_parts.append(f"  - {drug}: {effect}")
                    response_parts.append("")
                else:
                    response_parts.append("**🔗 Drug Interactions:** No known interactions listed.")
                    response_parts.append("")
            
            if any(word in query_lower for word in ['use', 'benefit', 'what', 'how', 'about', 'tell']):
                # Truncate description if too long
                desc = med['description']
                if len(desc) > 500:
                    desc = desc[:500] + "..."
                response_parts.append(f"**📋 Description:** {desc}")
                response_parts.append("")
            
            response_parts.append("---")
        
        return "\n".join(response_parts)
    
    def get_all_medicine_names(self) -> List[str]:
        """Get all medicine names for the dropdown"""
        if self.df.empty:
            return []
        return sorted(self.df['name'].tolist())


# Singleton instance
_medicine_search = None

def get_medicine_search() -> MedicineSearch:
    """Get or create the medicine search singleton"""
    global _medicine_search
    if _medicine_search is None:
        _medicine_search = MedicineSearch()
    return _medicine_search
