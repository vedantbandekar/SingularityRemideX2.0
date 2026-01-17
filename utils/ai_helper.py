import os
import json
import pandas as pd
from rapidfuzz import process, fuzz
from typing import List, Dict, Any, Union
from datetime import datetime

from utils.database import Database
from utils.ai_client import ask_ai_agent

class MedicineSearch:
    def __init__(self):
        self.db = Database()
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_medicine_data.csv')
        self.df = self._load_data()
        self.agent_id = os.getenv("LYZR_AGENT_ID")
        self.user_id = "default_user" # In a real app this would be dynamic
        self.session_id = "default_session"

    def _load_data(self) -> pd.DataFrame:
        try:
            if os.path.exists(self.data_path):
                return pd.read_csv(self.data_path)
            return pd.DataFrame()
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def search_medicine(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for medicines using fuzzy matching
        """
        if self.df.empty:
            return []

        # Get all medicine names
        names = self.df['name'].tolist()
        
        # Fuzzy match
        matches = process.extract(query, names, limit=limit, scorer=fuzz.WRatio)
        
        results = []
        for name, score, index in matches:
            if score > 50:  # Threshold
                row = self.df.iloc[index].to_dict()
                
                # Check for nan values and handle them
                cleaned_row = {}
                for k, v in row.items():
                    if pd.isna(v):
                        cleaned_row[k] = "Not available"
                    else:
                        cleaned_row[k] = v
                
                # Parse JSON fields
                for key in ['drug_interactions', 'side_effects']:
                    if key in cleaned_row and isinstance(cleaned_row[key], str):
                        try:
                            # Replace single quotes with double quotes if needed (simple heuristic)
                            val = cleaned_row[key]
                            if val.startswith("{") or val.startswith("["):
                                import ast
                                try:
                                    cleaned_row[key] = json.loads(val)
                                except:
                                    try:
                                        cleaned_row[key] = ast.literal_eval(val)
                                    except:
                                        pass
                        except:
                            pass
                
                # Add match score
                cleaned_row['match_score'] = round(score)
                results.append(cleaned_row)
                
        return results

    def answer_query(self, query: str) -> str:
        """
        Process user query, check for tools, execute if needed, or return AI response
        """
        
        system_instruction = """
        You are a smart medical assistant for the Remidex application.
        
        Your Capabilities:
        1. Answer questions about medicines (uses your internal knowledge).
        2. Manage the user's health data:
           - Add Medicine Schedule
           - Add Medicine Supply
           - Add Doctor Appointment
           - Add Health Vitals
        
        CRITICAL INSTRUCTION FOR TOOL USE:
        If the user wants to perform one of the above 4 actions, you MUST reply with a JSON object ONLY, and nothing else.
        
        JSON Formats:
        
        1. Add Medicine Schedule:
        {
            "action": "ADD_SCHEDULE",
            "data": {
                "name": "Medicine Name",
                "dosage": "e.g. 500mg",
                "frequency": "e.g. Twice daily"
            }
        }
        
        2. Add Medicine Supply:
        {
            "action": "ADD_SUPPLY",
            "data": {
                "medicine_name": "Medicine Name",
                "current_stock": 10 (integer),
                "daily_dosage": 2 (integer)
            }
        }
        
        3. Add Appointment:
        {
            "action": "ADD_APPOINTMENT",
            "data": {
                "doctor_name": "Dr. Name",
                "specialty": "Specialty",
                "appt_date": "YYYY-MM-DD",
                "appt_time": "HH:MM",
                "reason": "Reason"
            }
        }
        
        4. Add Vital:
        {
            "action": "ADD_VITAL",
            "data": {
                "date": "YYYY-MM-DD",
                "time": "HH:MM",
                "vital_type": "e.g. Blood Pressure",
                "value": "e.g. 120/80",
                "unit": "e.g. mmHg"
            }
        }
        
        If the user does NOT want to perform an action, just reply normally with helping text.
        """
        
        # Prepend instruction
        full_query = f"{system_instruction}\n\nUser Query: {query}"
        
        # Get AI response
        ai_response = ask_ai_agent(full_query, self.user_id, self.session_id)
        
        # Try to parse as JSON
        import re
        try:
            # First try to find a JSON code block
            json_match = re.search(r"```json(.*?)```", ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
            else:
                # Try to find a raw JSON object (assuming it starts with { and ends with })
                json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0).strip()
                else:
                    json_str = ai_response.strip()
            
            data = json.loads(json_str)
            
            if "action" in data and "data" in data:
                return self._execute_tool(data["action"], data["data"])
            
        except (json.JSONDecodeError, AttributeError):
            pass # Not a JSON response, just return normal text
            
        return ai_response

    def _execute_tool(self, action: str, data: Dict) -> str:
        try:
            if action == "ADD_SCHEDULE":
                self.db.add_medicine(
                    name=data.get("name", "Unknown"),
                    dosage=data.get("dosage", "Unknown"),
                    frequency=data.get("frequency", "Daily")
                )
                return f"✅ Successfully added medicine schedule for **{data.get('name')}**."
                
            elif action == "ADD_SUPPLY":
                self.db.add_supply(
                    medicine_name=data.get("medicine_name", "Unknown"),
                    current_stock=int(data.get("current_stock", 0)),
                    daily_dosage=int(data.get("daily_dosage", 1))
                )
                return f"✅ Successfully added supply for **{data.get('medicine_name')}**."
                
            elif action == "ADD_APPOINTMENT":
                self.db.add_appointment(
                    doctor_name=data.get("doctor_name", "Unknown"),
                    specialty=data.get("specialty", "General"),
                    appt_date=data.get("appt_date", datetime.now().strftime("%Y-%m-%d")),
                    appt_time=data.get("appt_time", "09:00"),
                    reason=data.get("reason", "Checkup")
                )
                return f"✅ Appointment booked with **{data.get('doctor_name')}** on {data.get('appt_date')}."
                
            elif action == "ADD_VITAL":
                self.db.add_vital(
                    date_str=data.get("date", datetime.now().strftime("%Y-%m-%d")),
                    time_str=data.get("time", datetime.now().strftime("%H:%M")),
                    vital_type=data.get("vital_type", "Unknown"),
                    value=data.get("value", "0"),
                    unit=data.get("unit", "-")
                )
                return f"✅ Recorded vital: **{data.get('vital_type')}** ({data.get('value')} {data.get('unit')})."
            
            else:
                return f"⚠️ Unknown action requested: {action}"
                
        except Exception as e:
            return f"❌ Error executing action: {str(e)}"

def get_medicine_search():
    """Factory function to return singleton instance"""
    if 'medicine_search_instance' not in globals():
        globals()['medicine_search_instance'] = MedicineSearch()
    return globals()['medicine_search_instance']
