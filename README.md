# ASRS Analysis Platform

Die **ASRS Analysis Platform** ist eine moderne Webanwendung zur Analyse von Aviation Safety Reporting System (ASRS) Berichten mit fortschrittlichen Natural Language Processing (NLP) Methoden. Ziel ist die automatisierte Extraktion, Klassifikation und Visualisierung motorbezogener Probleme aus Flugsicherheitsberichten, unterstützt durch ein intuitives Dashboard und umfangreiche Visualisierungen.

---

## 🚀 Features

- **CSV-Upload:** Einfache Übermittlung eigener ASRS-Datensätze
- **Automatische Vorverarbeitung:** Reinigung, Filterung und Aufbereitung der Daten
- **NLP-Analyse:** Integration modernster Modelle (KeyBERT, DistilBERT, BERT-BiLSTM-CRF, TF-IDF, LDA, SVM)
- **Modellvergleich:** Mehrere Modelle lassen sich direkt im Frontend vergleichen
- **Visualisierungen:** Balkendiagramme, Heatmaps, Zeitreihenplots & Wordclouds
- **Reporting:** Automatisierte Berichtsgenerierung für Analyseergebnisse
- **Intuitive UI:** Modernes, responsives React-Frontend mit Tailwind CSS
- **Live-Demo:** [ASRS Analysis Platform](https://ewqalxyg.manus.space)

---

## 🏗️ Technische Architektur

- **Backend:** Python 3.11, Flask REST API  
  - Endpunkte: `/api/asrs/upload`, `/api/asrs/preprocess`, `/api/asrs/analyze`, `/api/asrs/compare`, `/api/asrs/report`, `/api/asrs/health`
- **Frontend:** React (Vite), Tailwind CSS, shadcn/ui, Lucide Icons, Recharts
- **Deployment:** Vercel/Cloud, live erreichbar unter [ewqalxyg.manus.space](https://ewqalxyg.manus.space)

---

## ⚙️ Installation & Quickstart

> **Empfehlung:**  
> Die Installation der Python-Abhängigkeiten gelingt besonders einfach und schnell mit dem neuen [uv package manager](https://github.com/astral-sh/uv), der ein Drop-in-Ersatz für pip ist.  
> **Beispiel:**  
> ```bash
> uv pip install -r requirements.txt
> ```

### 1. Backend einrichten

```bash
git clone https://github.com/wac0ku/ASRS-Analysis.git
cd ASRS-Analysis/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Alternative schneller:
# uv pip install -r requirements.txt
python asrs.py
```

### 2. Frontend starten

```bash
cd ../frontend
npm install
npm run dev
```

### 3. Anwendung im Browser öffnen

`http://localhost:5173`

---

## 🖥️ Nutzung

1. **CSV-Upload:** ASRS-Datensatz im Frontend hochladen
2. **Modellwahl & Analyse:** Modell(e) auswählen → Analyse starten
3. **Ergebnisse visualisieren:** Dashboards & Berichte betrachten, exportieren oder speichern

---

## 📊 Funktionalitäten im Detail

- **Datenvorverarbeitung:** Automatische Filterung auf motorbezogene Berichte
- **NLP-Analyse:** Extraktion und Klassifikation sicherheitsrelevanter Themen
- **Modellvergleich:** Bewertung verschiedener ML/NLP-Ansätze anhand von Accuracy, Precision, Recall u.v.m.
- **Reporting:** Downloadbare Berichte (PDF/CSV) für Auswertung und Präsentation

---

## 🛡️ Qualität & Tests

- Umfassende Backend- und Frontend-Tests
- Edge-Case Handling, Fehlerbehandlung, Validierung auf allen Ebenen
- Performance geprüft (vollständiger Workflow < 10 Sekunden)
- Responsives, barrierefreies UI
- Modularer Aufbau für Erweiterbarkeit

---

## 📚 Weiterführende Dokumentation

- [ASRS_Analysis_Documentation.md](./ASRS_Analysis_Documentation.md)
- [Testprotokoll & Debugging](./test_protocol.md)

---

## 🎯 Zielgruppe & Use Cases

- Aviation Safety Analysten
- Data Scientists im Bereich Luftfahrt
- Studierende & Lehrende der Luft- und Raumfahrttechnik
- Entwickler:innen, die ML/NLP-Workflows in der Domäne Aviation Safety evaluieren möchten

---

## 🔑 SEO-Keywords

ASRS Analyse, Aviation Safety, NLP, Machine Learning, Flugsicherheitsberichte, CSV Analyse, Modellvergleich, Python Flask, React Dashboard, Datenvisualisierung, Safety Reporting, Luftfahrt, Incident Analysis

---

## 📝 Lizenz

MIT License – siehe [LICENSE](./LICENSE)

---

**Entwickelt von [wac0ku](https://github.com/wac0ku) • [Live-Demo ausprobieren!](https://ewqalxyg.manus.space)**
