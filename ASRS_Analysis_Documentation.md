# ASRS Analysis Platform - Projektdokumentation

## Projektübersicht

Die ASRS Analysis Platform ist eine Web-Anwendung zur Analyse von Aviation Safety Reporting System (ASRS) Berichten mit Fokus auf motorbezogene Probleme. Die Anwendung verwendet verschiedene NLP-Modelle zur Textanalyse und bietet umfassende Visualisierungen der Ergebnisse.

## Technische Architektur

### Backend (Flask)
- **Framework**: Flask mit Python 3.11
- **API-Endpunkte**:
  - `/api/asrs/upload` - CSV-Datei Upload
  - `/api/asrs/preprocess` - Datenvorverarbeitung
  - `/api/asrs/analyze` - NLP-Modell-Analyse
  - `/api/asrs/compare` - Modellvergleich
  - `/api/asrs/report` - Berichtsgenerierung
  - `/api/asrs/health` - Gesundheitscheck

### Frontend (React)
- **Framework**: React mit Vite
- **UI-Bibliotheken**: Tailwind CSS, shadcn/ui, Lucide Icons
- **Visualisierung**: Recharts für Diagramme
- **Deployment**: https://ewqalxyg.manus.space

### NLP-Modelle
1. **TF-IDF + SVM**: Textklassifikation mit Support Vector Machine
2. **KeyBERT**: BERT-basierte Keyword-Extraktion (optional)
3. **DistilBERT**: Sentiment-Analyse (optional)
4. **LDA**: Latent Dirichlet Allocation für Topic-Modelling (optional)

## Funktionalitäten

### 1. Daten-Upload
- CSV-Datei Upload mit Drag & Drop
- Automatische Validierung der Dateiformate
- Vorschau der hochgeladenen Daten

### 2. Datenvorverarbeitung
- Filterung nach motorbezogenen Keywords
- Standardisierung von Flugzeugtypen und Flugphasen
- Textvorverarbeitung und -bereinigung
- Extraktion von Datums-Features

### 3. NLP-Analyse
- Auswahl verschiedener Modelle
- Automatische Klassifikation von Problemkategorien
- Keyword-Extraktion
- Topic-Modelling
- Sentiment-Analyse

### 4. Visualisierung
- Balkendiagramme für Modellgenauigkeit
- Kreisdiagramme für Kategorienverteilung
- Zeitreihenanalysen
- Keyword-Häufigkeitsdiagramme

### 5. Dashboard & Reporting
- Übersichtsdashboard mit Key-Metrics
- Automatische Berichtsgenerierung
- Download-Funktionalität für Berichte

## Installation und Setup

### Backend
```bash
cd asrs-analysis-backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend
```bash
cd asrs-analysis-frontend
npm install
npm run dev
```

## Verwendung

1. **Upload**: Laden Sie eine CSV-Datei mit ASRS-Berichten hoch
2. **Analyse**: Wählen Sie die gewünschten NLP-Modelle aus
3. **Ergebnisse**: Betrachten Sie die Visualisierungen der Analyseergebnisse
4. **Dashboard**: Generieren Sie einen detaillierten Bericht

## Beispieldaten

Die Anwendung wurde mit synthetischen ASRS-Daten getestet, die typische motorbezogene Probleme abbilden:
- Engine-Ausfälle
- Vibrationen
- Temperaturanomalien
- Kraftstoffsystem-Probleme
- Wartungsprobleme

## Deployment

- **Frontend**: Deployed auf https://ewqalxyg.manus.space
- **Backend**: Läuft lokal (Port 5002) - Deployment mit schweren ML-Dependencies nicht möglich

## Technische Herausforderungen

1. **ML-Dependencies**: Transformers und PyTorch sind zu groß für Standard-Deployment
2. **CORS-Konfiguration**: Notwendig für Frontend-Backend-Kommunikation
3. **Performance**: Große Modelle benötigen Optimierung für Produktionsumgebung

## Empfehlungen für Produktionsumgebung

1. **Backend-Deployment**: Verwendung von Cloud-Services mit GPU-Unterstützung
2. **Caching**: Implementierung von Redis für Modell-Caching
3. **Skalierung**: Microservices-Architektur für bessere Skalierbarkeit
4. **Monitoring**: Logging und Monitoring für Produktionsumgebung

## Fazit

Die ASRS Analysis Platform demonstriert erfolgreich die Anwendung verschiedener NLP-Techniken zur Analyse von Aviation Safety Reports. Die modulare Architektur ermöglicht einfache Erweiterungen und Anpassungen für verschiedene Anwendungsfälle.

**Live-Demo**: https://ewqalxyg.manus.space

---
*Entwickelt für die Analyse motorbezogener Probleme in ASRS-Berichten*

