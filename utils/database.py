"""
Database utility module for Remidex
Handles all SQLite CRUD operations for medicines, alerts, supplies, and history
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'remidex.db')


class Database:
    """SQLite database handler for Remidex application"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def _init_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create medicines table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                frequency TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_id INTEGER NOT NULL,
                alert_time TEXT NOT NULL,
                FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
            )
        ''')
        
        # Create supplies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL UNIQUE,
                current_stock INTEGER NOT NULL,
                daily_dosage INTEGER NOT NULL,
                alert_threshold INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                taken_date DATE NOT NULL,
                taken_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create vitals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                time TEXT NOT NULL,
                vital_type TEXT NOT NULL,
                value TEXT NOT NULL,
                unit TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_name TEXT NOT NULL,
                specialty TEXT NOT NULL,
                appt_date DATE NOT NULL,
                appt_time TEXT NOT NULL,
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== MEDICINES CRUD ====================
    
    def add_medicine(self, name: str, dosage: str, frequency: str) -> int:
        """Add a new medicine and return its ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO medicines (name, dosage, frequency) VALUES (?, ?, ?)",
            (name, dosage, frequency)
        )
        medicine_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return medicine_id
    
    def get_all_medicines(self) -> List[Dict]:
        """Get all medicines with their alerts"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.*, GROUP_CONCAT(a.alert_time) as alert_times
            FROM medicines m
            LEFT JOIN alerts a ON m.id = a.medicine_id
            GROUP BY m.id
            ORDER BY m.created_at DESC
        ''')
        medicines = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Parse alert times
        for med in medicines:
            if med['alert_times']:
                med['alert_times'] = med['alert_times'].split(',')
            else:
                med['alert_times'] = []
        
        return medicines
    
    def delete_medicine(self, medicine_id: int):
        """Delete a medicine by ID (alerts deleted via CASCADE)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
        conn.commit()
        conn.close()
    
    # ==================== ALERTS CRUD ====================
    
    def add_alert(self, medicine_id: int, alert_time: str):
        """Add an alert time for a medicine"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (medicine_id, alert_time) VALUES (?, ?)",
            (medicine_id, alert_time)
        )
        conn.commit()
        conn.close()
    
    def get_alerts_for_medicine(self, medicine_id: int) -> List[str]:
        """Get all alert times for a medicine"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT alert_time FROM alerts WHERE medicine_id = ?",
            (medicine_id,)
        )
        alerts = [row['alert_time'] for row in cursor.fetchall()]
        conn.close()
        return alerts
    
    def delete_alert(self, alert_id: int):
        """Delete an alert by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
    
    # ==================== SUPPLIES CRUD ====================
    
    def add_supply(self, medicine_name: str, current_stock: int, 
                   daily_dosage: int, alert_threshold: int = 3) -> bool:
        """Add or update medicine supply. Returns True if successful."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO supplies (medicine_name, current_stock, daily_dosage, alert_threshold)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(medicine_name) DO UPDATE SET
                    current_stock = excluded.current_stock,
                    daily_dosage = excluded.daily_dosage,
                    alert_threshold = excluded.alert_threshold
            ''', (medicine_name, current_stock, daily_dosage, alert_threshold))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    
    def get_all_supplies(self) -> List[Dict]:
        """Get all medicine supplies"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM supplies ORDER BY created_at DESC")
        supplies = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return supplies
    
    def update_supply_stock(self, medicine_name: str, new_stock: int):
        """Update the stock count for a medicine"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE supplies SET current_stock = ? WHERE medicine_name = ?",
            (new_stock, medicine_name)
        )
        conn.commit()
        conn.close()
    
    def decrement_supply(self, medicine_name: str, amount: int = 1) -> bool:
        """Decrement supply by amount. Returns True if successful."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT current_stock FROM supplies WHERE medicine_name = ?",
            (medicine_name,)
        )
        row = cursor.fetchone()
        if row and row['current_stock'] >= amount:
            new_stock = row['current_stock'] - amount
            cursor.execute(
                "UPDATE supplies SET current_stock = ? WHERE medicine_name = ?",
                (new_stock, medicine_name)
            )
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    
    def delete_supply(self, supply_id: int):
        """Delete a supply entry by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM supplies WHERE id = ?", (supply_id,))
        conn.commit()
        conn.close()
    
    # ==================== HISTORY CRUD ====================
    
    def add_history(self, medicine_name: str, taken_date: str = None, taken_time: str = None):
        """Log a medicine intake to history"""
        if taken_date is None:
            taken_date = date.today().isoformat()
        if taken_time is None:
            taken_time = datetime.now().strftime("%H:%M")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (medicine_name, taken_date, taken_time) VALUES (?, ?, ?)",
            (medicine_name, taken_date, taken_time)
        )
        conn.commit()
        conn.close()
    
    def get_all_history(self) -> List[Dict]:
        """Get all history entries"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY taken_date DESC, taken_time DESC")
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history
    
    def get_today_history(self) -> List[Dict]:
        """Get history entries for today"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM history WHERE taken_date = ? ORDER BY taken_time DESC",
            (today,)
        )
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history
    
    def delete_history(self, history_id: int):
        """Delete a history entry by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE id = ?", (history_id,))
        conn.commit()
        conn.close()
    
    def clear_all_history(self):
        """Delete all history entries"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()
    
    def is_medicine_taken_today(self, medicine_name: str, alert_time: str) -> bool:
        """Check if a specific medicine was taken at a specific time today"""
        today = date.today().isoformat()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM history WHERE medicine_name = ? AND taken_date = ? AND taken_time = ?",
            (medicine_name, today, alert_time)
        )
        result = cursor.fetchone()
        conn.close()
        return result['count'] > 0

    def get_streak_days(self) -> int:
        """Calculate the current streak of consecutive days with medication taken"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all unique dates from history, sorted descending
        cursor.execute("SELECT DISTINCT taken_date FROM history ORDER BY taken_date DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0
            
        dates = [row['taken_date'] for row in rows]
        today_str = date.today().isoformat()
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()
        
        streak = 0
        current_check = date.today()
        
        # If no entry for today yet, check relative to yesterday?
        # Standard streak logic: if today is empty, streak is maintained if yesterday was done.
        # But for 'Current Streak', usually counts up to today.
        # Let's count backwards from today IF today has entry, OR from yesterday.
        
        has_today = today_str in dates
        if not has_today:
            # If today not done, start checking from yesterday. 
            # If yesterday missing too, streak is 0.
            current_check = date.today() - timedelta(days=1)
            if current_check.isoformat() not in dates:
                return 0
        
        # Calculate streak
        while True:
            check_str = current_check.isoformat()
            if check_str in dates:
                streak += 1
                current_check = current_check - timedelta(days=1)
            else:
                break
                
        return streak

    # ==================== VITALS CRUD ====================

    def add_vital(self, date_str: str, time_str: str, vital_type: str, value: str, unit: str, notes: str = ""):
        """Log a health vital"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vitals (date, time, vital_type, value, unit, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (date_str, time_str, vital_type, value, unit, notes)
        )
        conn.commit()
        conn.close()

    def get_all_vitals(self) -> List[Dict]:
        """Get all vitals ordered by date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vitals ORDER BY date DESC, time DESC")
        vitals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return vitals

    def delete_vital(self, vital_id: int):
        """Delete a vital entry"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vitals WHERE id = ?", (vital_id,))
        conn.commit()
        conn.close()

    # ==================== APPOINTMENTS CRUD ====================

    def add_appointment(self, doctor_name: str, specialty: str, appt_date: str, appt_time: str, reason: str, notes: str = ""):
        """Add a doctor appointment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (doctor_name, specialty, appt_date, appt_time, reason, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (doctor_name, specialty, appt_date, appt_time, reason, notes)
        )
        conn.commit()
        conn.close()

    def get_all_appointments(self) -> List[Dict]:
        """Get all appointments ordered by date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments ORDER BY appt_date ASC, appt_time ASC")
        appts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return appts

    def delete_appointment(self, appt_id: int):
        """Delete an appointment"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appt_id,))
        conn.commit()
        conn.close()
