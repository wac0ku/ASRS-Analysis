from flask import Blueprint, request, jsonify, current_app
import pandas as pd
import os
import json
from werkzeug.utils import secure_filename
import logging
from src.asrs_data_processor import ASRSDataProcessor
from src.model_comparer import ModelComparer

# Blueprint für ASRS-Analyse-Routen
asrs_bp = Blueprint('asrs', __name__)

# Konfiguration
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt'}

# Stelle sicher, dass Upload-Ordner existiert
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Globale Instanzen
data_processor = ASRSDataProcessor()
model_comparer = ModelComparer()

# Temporärer Speicher für verarbeitete Daten
processed_data_store = {}

def allowed_file(filename):
    """Überprüft, ob die Datei-Erweiterung erlaubt ist."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@asrs_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpunkt zum Hochladen von ASRS-CSV-Dateien.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Keine Datei gefunden'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Keine Datei ausgewählt'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Versuche die Datei zu laden und grundlegende Info zu extrahieren
            try:
                df = pd.read_csv(filepath)
                
                # Validierung: Datei darf nicht leer sein
                if len(df) == 0:
                    return jsonify({
                        'error': 'Die hochgeladene CSV-Datei ist leer. Bitte laden Sie eine Datei mit Daten hoch.'
                    }), 400
                
                # Validierung: Mindestens eine der erwarteten Textspalten sollte vorhanden sein
                expected_text_columns = ['narrative', 'synopsis', 'problem_description', 'text', 'description']
                available_text_columns = [col for col in expected_text_columns if col in df.columns]
                
                if not available_text_columns:
                    return jsonify({
                        'error': f'Keine der erwarteten Textspalten gefunden. Erwartete Spalten: {expected_text_columns}. Gefundene Spalten: {list(df.columns)}'
                    }), 400
                
                file_info = {
                    'filename': filename,
                    'filepath': filepath,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'available_text_columns': available_text_columns,
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
                
                return jsonify({
                    'message': 'Datei erfolgreich hochgeladen und validiert',
                    'file_info': file_info
                }), 200
                
            except Exception as e:
                return jsonify({'error': f'Fehler beim Lesen der CSV-Datei: {str(e)}'}), 400
        
        return jsonify({'error': 'Dateityp nicht erlaubt'}), 400
        
    except Exception as e:
        current_app.logger.error(f"Upload-Fehler: {e}")
        return jsonify({'error': f'Upload-Fehler: {str(e)}'}), 500

@asrs_bp.route('/preprocess', methods=['POST'])
def preprocess_data():
    """
    Endpunkt zur Datenvorverarbeitung.
    """
    try:
        data = request.get_json()
        
        if not data or 'filepath' not in data:
            return jsonify({'error': 'Dateipfad erforderlich'}), 400
        
        filepath = data['filepath']
        text_columns = data.get('text_columns', None)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        # Daten laden
        df = data_processor.load_data(filepath)
        
        # Validierung: Datei darf nicht leer sein
        if len(df) == 0:
            return jsonify({
                'error': 'Die Datei enthält keine Daten zum Verarbeiten.'
            }), 400
        
        # Datenvorverarbeitung durchführen
        result = data_processor.process_data(df, text_columns)
        
        # Validierung: Überprüfe ob motorbezogene Berichte gefunden wurden
        if result['stats']['filtered_count'] == 0:
            return jsonify({
                'error': 'Keine motorbezogenen Berichte in den Daten gefunden. Überprüfen Sie, ob die Daten relevante Textspalten enthalten.',
                'stats': result['stats'],
                'suggestions': [
                    'Stellen Sie sicher, dass die Textspalten motorbezogene Begriffe enthalten',
                    'Überprüfen Sie die Spalten: narrative, synopsis, problem_description',
                    'Verwenden Sie Begriffe wie: engine, motor, turbine, compressor, etc.'
                ]
            }), 400
        
        # Warnung bei niedriger Filterrate
        warnings = []
        if result['stats']['filter_ratio'] < 0.1:
            warnings.append(f"Niedrige Filterrate ({result['stats']['filter_ratio']*100:.1f}%). Möglicherweise enthält die Datei wenige motorbezogene Berichte.")
        
        # Verarbeitete Daten temporär speichern
        session_id = f"session_{len(processed_data_store)}"
        processed_data_store[session_id] = {
            'data': result['data'],
            'stats': result['stats'],
            'filepath': filepath
        }
        
        # Statistiken für Response vorbereiten
        response_stats = result['stats'].copy()
        response_stats['session_id'] = session_id
        
        # Sample der verarbeiteten Daten
        sample_data = result['data'].head(5).to_dict('records') if len(result['data']) > 0 else []
        
        response = {
            'message': 'Datenvorverarbeitung erfolgreich',
            'session_id': session_id,
            'stats': response_stats,
            'sample_data': sample_data,
            'processed_columns': list(result['data'].columns)
        }
        
        if warnings:
            response['warnings'] = warnings
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Preprocessing-Fehler: {e}")
        return jsonify({'error': f'Preprocessing-Fehler: {str(e)}'}), 500

@asrs_bp.route('/analyze', methods=['POST'])
def analyze_data():
    """
    Endpunkt zur Analyse mit verschiedenen NLP-Modellen.
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Session-ID erforderlich'}), 400
        
        session_id = data['session_id']
        text_column = data.get('text_column', 'narrative')
        target_column = data.get('target_column', None)
        models_to_run = data.get('models', ['tfidf_svm'])
        
        # Validierung: Modell-Liste darf nicht leer sein
        if not models_to_run or len(models_to_run) == 0:
            return jsonify({'error': 'Mindestens ein Modell muss ausgewählt werden'}), 400
        
        # Validierung: Überprüfe verfügbare Modelle
        available_models = model_comparer.get_available_models()
        invalid_models = [model for model in models_to_run if model not in available_models]
        if invalid_models:
            return jsonify({
                'error': f'Ungültige Modelle: {invalid_models}. Verfügbare Modelle: {available_models}'
            }), 400
        
        if session_id not in processed_data_store:
            return jsonify({'error': 'Session nicht gefunden'}), 404
        
        # Verarbeitete Daten abrufen
        session_data = processed_data_store[session_id]
        df = session_data['data']
        
        # Validierung: Datensatz darf nicht leer sein
        if len(df) == 0:
            return jsonify({'error': 'Keine Daten in der Session verfügbar'}), 400
        
        # Verfügbare Textspalten prüfen
        available_text_columns = [col for col in df.columns if 'text' in col.lower() or 'narrative' in col.lower()]
        if text_column not in df.columns and available_text_columns:
            text_column = available_text_columns[0]
        
        if text_column not in df.columns:
            return jsonify({'error': f'Textspalte {text_column} nicht gefunden'}), 400
        
        # Modellvergleich durchführen
        analysis_results = model_comparer.compare_models(df, text_column, target_column)
        
        # Ergebnisse in Session speichern
        processed_data_store[session_id]['analysis_results'] = analysis_results
        
        return jsonify({
            'message': 'Analyse erfolgreich durchgeführt',
            'session_id': session_id,
            'results': analysis_results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Analyse-Fehler: {e}")
        return jsonify({'error': f'Analyse-Fehler: {str(e)}'}), 500

@asrs_bp.route('/compare', methods=['POST'])
def compare_models():
    """
    Endpunkt zum Vergleich der Modellleistungen.
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Session-ID erforderlich'}), 400
        
        session_id = data['session_id']
        
        if session_id not in processed_data_store:
            return jsonify({'error': 'Session nicht gefunden'}), 404
        
        session_data = processed_data_store[session_id]
        
        if 'analysis_results' not in session_data:
            return jsonify({'error': 'Keine Analyseergebnisse gefunden. Führen Sie zuerst eine Analyse durch.'}), 400
        
        analysis_results = session_data['analysis_results']
        
        # Detaillierte Vergleichsmetriken erstellen
        comparison_data = {
            'model_performance': {},
            'visualization_data': {},
            'recommendations': analysis_results.get('comparison_summary', {}).get('recommendations', [])
        }
        
        # Performance-Metriken extrahieren
        for model_name, results in analysis_results.get('model_results', {}).items():
            if 'error' not in results:
                model_perf = {
                    'name': results.get('model_name', model_name),
                    'type': 'classification' if 'accuracy' in results else 'analysis'
                }
                
                if 'accuracy' in results:
                    model_perf['accuracy'] = results['accuracy']
                    model_perf['confusion_matrix'] = results.get('confusion_matrix', [])
                
                if 'top_keywords_by_frequency' in results:
                    model_perf['top_keywords'] = results['top_keywords_by_frequency'][:10]
                
                if 'topics' in results:
                    model_perf['topics'] = results['topics']
                
                if 'sentiment_distribution' in results:
                    model_perf['sentiment_distribution'] = results['sentiment_distribution']
                
                comparison_data['model_performance'][model_name] = model_perf
        
        # Visualisierungsdaten vorbereiten
        comparison_data['visualization_data'] = {
            'accuracy_comparison': [],
            'keyword_frequency': [],
            'topic_distribution': [],
            'sentiment_analysis': []
        }
        
        # Genauigkeitsvergleich
        for model_name, perf in comparison_data['model_performance'].items():
            if 'accuracy' in perf:
                comparison_data['visualization_data']['accuracy_comparison'].append({
                    'model': perf['name'],
                    'accuracy': perf['accuracy']
                })
        
        # Keyword-Häufigkeiten (von KeyBERT)
        if 'keybert' in comparison_data['model_performance']:
            keybert_data = comparison_data['model_performance']['keybert']
            if 'top_keywords' in keybert_data:
                comparison_data['visualization_data']['keyword_frequency'] = [
                    {'keyword': kw[0], 'frequency': kw[1]} for kw in keybert_data['top_keywords']
                ]
        
        return jsonify({
            'message': 'Modellvergleich erfolgreich',
            'session_id': session_id,
            'comparison': comparison_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Vergleichs-Fehler: {e}")
        return jsonify({'error': f'Vergleichs-Fehler: {str(e)}'}), 500

@asrs_bp.route('/report', methods=['POST'])
def generate_report():
    """
    Endpunkt zur Generierung eines Berichts.
    """
    try:
        data = request.get_json()
        
        if not data or 'session_id' not in data:
            return jsonify({'error': 'Session-ID erforderlich'}), 400
        
        session_id = data['session_id']
        
        if session_id not in processed_data_store:
            return jsonify({'error': 'Session nicht gefunden'}), 404
        
        session_data = processed_data_store[session_id]
        
        # Bericht erstellen
        report = {
            'title': 'ASRS Motorbezogene Probleme - Analysebericht',
            'generated_at': pd.Timestamp.now().isoformat(),
            'data_summary': session_data.get('stats', {}),
            'analysis_results': session_data.get('analysis_results', {}),
            'recommendations': [],
            'conclusions': []
        }
        
        # Empfehlungen basierend auf Ergebnissen
        if 'analysis_results' in session_data:
            analysis = session_data['analysis_results']
            
            # Datenqualität bewerten
            stats = session_data.get('stats', {})
            filter_ratio = stats.get('filter_ratio', 0)
            
            if filter_ratio < 0.1:
                report['recommendations'].append(
                    "Niedrige Filterrate für motorbezogene Probleme. Überprüfen Sie die Keyword-Liste oder Datenqualität."
                )
            elif filter_ratio > 0.3:
                report['recommendations'].append(
                    "Hohe Filterrate für motorbezogene Probleme. Die Daten enthalten viele relevante Berichte."
                )
            
            # Modellleistung bewerten
            model_results = analysis.get('model_results', {})
            
            if 'tfidf_svm' in model_results and 'accuracy' in model_results['tfidf_svm']:
                accuracy = model_results['tfidf_svm']['accuracy']
                if accuracy > 0.8:
                    report['recommendations'].append(
                        "TF-IDF + SVM zeigt hohe Klassifikationsgenauigkeit. Empfohlen für automatische Kategorisierung."
                    )
                else:
                    report['recommendations'].append(
                        "TF-IDF + SVM zeigt moderate Genauigkeit. Erwägen Sie Feature-Engineering oder mehr Trainingsdaten."
                    )
            
            if 'keybert' in model_results:
                report['recommendations'].append(
                    "KeyBERT eignet sich gut für die Extraktion relevanter Keywords aus Berichten."
                )
            
            # Schlussfolgerungen
            report['conclusions'].append(
                f"Analysiert wurden {stats.get('final_count', 0)} motorbezogene ASRS-Berichte."
            )
            
            if len(model_results) > 1:
                report['conclusions'].append(
                    f"Vergleich von {len(model_results)} verschiedenen NLP-Modellen durchgeführt."
                )
        
        return jsonify({
            'message': 'Bericht erfolgreich generiert',
            'session_id': session_id,
            'report': report
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Bericht-Fehler: {e}")
        return jsonify({'error': f'Bericht-Fehler: {str(e)}'}), 500

@asrs_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    Endpunkt zum Auflisten aller aktiven Sessions.
    """
    try:
        sessions = []
        for session_id, data in processed_data_store.items():
            session_info = {
                'session_id': session_id,
                'filepath': data.get('filepath', ''),
                'stats': data.get('stats', {}),
                'has_analysis': 'analysis_results' in data
            }
            sessions.append(session_info)
        
        return jsonify({
            'sessions': sessions,
            'total_sessions': len(sessions)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Sessions-Fehler: {e}")
        return jsonify({'error': f'Sessions-Fehler: {str(e)}'}), 500

@asrs_bp.route('/health', methods=['GET'])
def health_check():
    """
    Gesundheitscheck für die API.
    """
    return jsonify({
        'status': 'healthy',
        'message': 'ASRS Analysis API ist betriebsbereit',
        'available_models': list(model_comparer.models.keys()),
        'upload_folder': UPLOAD_FOLDER
    }), 200

