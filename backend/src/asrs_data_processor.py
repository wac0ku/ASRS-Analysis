import pandas as pd
import numpy as np
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

class ASRSDataProcessor:
    """
    Klasse für die Vorverarbeitung von ASRS-Daten mit Fokus auf motorbezogene Probleme.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.motor_keywords = [
            'engine', 'motor', 'turbine', 'compressor', 'combustor', 'fan', 'rotor',
            'stator', 'blade', 'vane', 'nozzle', 'thrust', 'power', 'rpm', 'egt',
            'fuel', 'oil', 'hydraulic', 'pneumatic', 'bleed', 'starter', 'ignition',
            'vibration', 'surge', 'stall', 'flameout', 'shutdown', 'failure',
            'malfunction', 'anomaly', 'warning', 'caution', 'alert'
        ]
        
        self.aircraft_types = {
            'boeing': ['b737', 'b747', 'b757', 'b767', 'b777', 'b787'],
            'airbus': ['a319', 'a320', 'a321', 'a330', 'a340', 'a350', 'a380'],
            'embraer': ['e170', 'e175', 'e190', 'e195'],
            'bombardier': ['crj', 'dash'],
            'other': ['md80', 'md90', 'dc9', 'dc10']
        }
        
        self.flight_phases = [
            'taxi', 'takeoff', 'climb', 'cruise', 'descent', 'approach', 'landing',
            'ground', 'parked', 'maintenance'
        ]
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Lädt ASRS-Daten aus einer CSV-Datei.
        
        Args:
            file_path: Pfad zur CSV-Datei
            
        Returns:
            DataFrame mit den geladenen Daten
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Daten erfolgreich geladen: {len(df)} Zeilen")
            return df
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Daten: {e}")
            raise
    
    def filter_motor_related(self, df: pd.DataFrame, text_columns: List[str] = None) -> pd.DataFrame:
        """
        Filtert Berichte nach motorbezogenen Problemen.
        
        Args:
            df: Input DataFrame
            text_columns: Liste der Textspalten zum Durchsuchen
            
        Returns:
            Gefiltertes DataFrame
        """
        if text_columns is None:
            # Standardspalten für ASRS-Berichte
            text_columns = ['narrative', 'synopsis', 'problem_description', 'text']
        
        # Verfügbare Textspalten finden
        available_columns = [col for col in text_columns if col in df.columns]
        
        if not available_columns:
            self.logger.warning("Keine Textspalten gefunden, verwende alle Spalten")
            available_columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # Motor-Keywords in allen verfügbaren Textspalten suchen
        motor_mask = pd.Series([False] * len(df))
        
        for col in available_columns:
            if col in df.columns:
                col_text = df[col].fillna('').astype(str).str.lower()
                for keyword in self.motor_keywords:
                    motor_mask |= col_text.str.contains(keyword, case=False, na=False)
        
        filtered_df = df[motor_mask].copy()
        self.logger.info(f"Motorbezogene Berichte gefiltert: {len(filtered_df)} von {len(df)}")
        
        return filtered_df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Behandelt fehlende Werte in den Daten.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame mit behandelten fehlenden Werten
        """
        df_clean = df.copy()
        
        # Numerische Spalten mit Median füllen
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
        
        # Textspalten mit 'Unknown' füllen
        text_columns = df_clean.select_dtypes(include=['object']).columns
        for col in text_columns:
            df_clean[col].fillna('Unknown', inplace=True)
        
        self.logger.info("Fehlende Werte behandelt")
        return df_clean
    
    def standardize_aircraft_type(self, df: pd.DataFrame, aircraft_column: str = 'aircraft_type') -> pd.DataFrame:
        """
        Standardisiert Flugzeugtypen.
        
        Args:
            df: Input DataFrame
            aircraft_column: Name der Flugzeugtypenspalte
            
        Returns:
            DataFrame mit standardisierten Flugzeugtypen
        """
        if aircraft_column not in df.columns:
            self.logger.warning(f"Spalte {aircraft_column} nicht gefunden")
            return df
        
        df_std = df.copy()
        df_std[aircraft_column] = df_std[aircraft_column].fillna('Unknown').astype(str).str.lower()
        
        # Standardisierung basierend auf bekannten Flugzeugtypen
        def standardize_type(aircraft_type):
            aircraft_type = aircraft_type.lower().strip()
            
            for manufacturer, types in self.aircraft_types.items():
                for ac_type in types:
                    if ac_type in aircraft_type:
                        return f"{manufacturer}_{ac_type}"
            
            return 'other'
        
        df_std[f'{aircraft_column}_standardized'] = df_std[aircraft_column].apply(standardize_type)
        
        self.logger.info("Flugzeugtypen standardisiert")
        return df_std
    
    def standardize_flight_phase(self, df: pd.DataFrame, phase_column: str = 'flight_phase') -> pd.DataFrame:
        """
        Standardisiert Flugphasen.
        
        Args:
            df: Input DataFrame
            phase_column: Name der Flugphasenspalte
            
        Returns:
            DataFrame mit standardisierten Flugphasen
        """
        if phase_column not in df.columns:
            self.logger.warning(f"Spalte {phase_column} nicht gefunden")
            return df
        
        df_std = df.copy()
        df_std[phase_column] = df_std[phase_column].fillna('Unknown').astype(str).str.lower()
        
        def standardize_phase(phase):
            phase = phase.lower().strip()
            
            for std_phase in self.flight_phases:
                if std_phase in phase:
                    return std_phase
            
            return 'other'
        
        df_std[f'{phase_column}_standardized'] = df_std[phase_column].apply(standardize_phase)
        
        self.logger.info("Flugphasen standardisiert")
        return df_std
    
    def extract_date_features(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """
        Extrahiert Datums-Features für Jahresanalyse.
        
        Args:
            df: Input DataFrame
            date_column: Name der Datumsspalte
            
        Returns:
            DataFrame mit extrahierten Datums-Features
        """
        if date_column not in df.columns:
            self.logger.warning(f"Spalte {date_column} nicht gefunden")
            return df
        
        df_date = df.copy()
        
        # Datum parsen
        df_date[date_column] = pd.to_datetime(df_date[date_column], errors='coerce')
        
        # Features extrahieren
        df_date['year'] = df_date[date_column].dt.year
        df_date['month'] = df_date[date_column].dt.month
        df_date['quarter'] = df_date[date_column].dt.quarter
        df_date['day_of_week'] = df_date[date_column].dt.dayofweek
        
        self.logger.info("Datums-Features extrahiert")
        return df_date
    
    def preprocess_text(self, text: str) -> str:
        """
        Vorverarbeitung von Textdaten.
        
        Args:
            text: Input-Text
            
        Returns:
            Vorverarbeiteter Text
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Text zu Kleinbuchstaben
        text = str(text).lower()
        
        # Sonderzeichen entfernen (außer Buchstaben, Zahlen und Leerzeichen)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Mehrfache Leerzeichen durch einzelne ersetzen
        text = re.sub(r'\s+', ' ', text)
        
        # Führende und nachfolgende Leerzeichen entfernen
        text = text.strip()
        
        return text
    
    def process_data(self, df: pd.DataFrame, text_columns: List[str] = None) -> Dict:
        """
        Vollständige Datenvorverarbeitung.
        
        Args:
            df: Input DataFrame
            text_columns: Liste der Textspalten
            
        Returns:
            Dictionary mit verarbeiteten Daten und Statistiken
        """
        self.logger.info("Starte Datenvorverarbeitung")
        
        # 1. Motorbezogene Berichte filtern
        df_filtered = self.filter_motor_related(df, text_columns)
        
        # 2. Fehlende Werte behandeln
        df_clean = self.handle_missing_values(df_filtered)
        
        # 3. Flugzeugtypen standardisieren
        if 'aircraft_type' in df_clean.columns:
            df_clean = self.standardize_aircraft_type(df_clean)
        
        # 4. Flugphasen standardisieren
        if 'flight_phase' in df_clean.columns:
            df_clean = self.standardize_flight_phase(df_clean)
        
        # 5. Datums-Features extrahieren
        date_columns = [col for col in df_clean.columns if 'date' in col.lower()]
        if date_columns:
            df_clean = self.extract_date_features(df_clean, date_columns[0])
        
        # 6. Text vorverarbeiten
        if text_columns:
            available_text_columns = [col for col in text_columns if col in df_clean.columns]
            for col in available_text_columns:
                df_clean[f'{col}_processed'] = df_clean[col].apply(self.preprocess_text)
        
        # Statistiken erstellen
        stats = {
            'original_count': len(df),
            'filtered_count': len(df_filtered),
            'final_count': len(df_clean),
            'filter_ratio': len(df_filtered) / len(df) if len(df) > 0 else 0,
            'columns': list(df_clean.columns),
            'motor_keywords_found': self.motor_keywords
        }
        
        self.logger.info("Datenvorverarbeitung abgeschlossen")
        
        return {
            'data': df_clean,
            'stats': stats
        }

