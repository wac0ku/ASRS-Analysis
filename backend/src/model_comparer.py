import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    from keybert import KeyBERT
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers oder KeyBERT nicht verfügbar. Einige Modelle werden nicht funktionieren.")

try:
    from gensim import corpora
    from gensim.models import LdaModel
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    logging.warning("Gensim nicht verfügbar. LDA-Modell wird nicht funktionieren.")

class ModelComparer:
    """
    Klasse für den Vergleich verschiedener NLP-Modelle zur Analyse von ASRS-Berichten.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.results = {}
        self.vectorizers = {}
        
        # Initialisiere verfügbare Modelle
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialisiert die verfügbaren NLP-Modelle."""
        
        # TF-IDF + SVM
        self.models['tfidf_svm'] = {
            'name': 'TF-IDF + SVM',
            'vectorizer': TfidfVectorizer(max_features=5000, stop_words='english'),
            'classifier': SVC(kernel='rbf', random_state=42),
            'type': 'classification'
        }
        
        # LDA Topic Modeling
        if GENSIM_AVAILABLE:
            self.models['lda'] = {
                'name': 'Latent Dirichlet Allocation',
                'model': None,  # Wird später initialisiert
                'type': 'topic_modeling'
            }
        
        # KeyBERT für Keyword-Extraktion
        if TRANSFORMERS_AVAILABLE:
            try:
                self.models['keybert'] = {
                    'name': 'KeyBERT',
                    'model': KeyBERT(),
                    'type': 'keyword_extraction'
                }
            except Exception as e:
                self.logger.warning(f"KeyBERT konnte nicht initialisiert werden: {e}")
        
        # DistilBERT für Klassifikation
        if TRANSFORMERS_AVAILABLE:
            try:
                self.models['distilbert'] = {
                    'name': 'DistilBERT',
                    'model': pipeline('text-classification', 
                                    model='distilbert-base-uncased-finetuned-sst-2-english'),
                    'type': 'classification'
                }
            except Exception as e:
                self.logger.warning(f"DistilBERT konnte nicht initialisiert werden: {e}")
        
        self.logger.info(f"Initialisierte Modelle: {list(self.models.keys())}")
    
    def get_available_models(self) -> List[str]:
        """
        Gibt eine Liste der verfügbaren Modelle zurück.
        
        Returns:
            Liste der verfügbaren Modell-Namen
        """
        return list(self.models.keys())
    
    def prepare_classification_data(self, df: pd.DataFrame, text_column: str, 
                                  target_column: str = None) -> Tuple[List[str], List[str]]:
        """
        Bereitet Daten für Klassifikationsaufgaben vor.
        
        Args:
            df: Input DataFrame
            text_column: Name der Textspalte
            target_column: Name der Zielspalte (falls vorhanden)
            
        Returns:
            Tuple von (Texte, Labels)
        """
        texts = df[text_column].fillna('').astype(str).tolist()
        
        if target_column and target_column in df.columns:
            labels = df[target_column].fillna('unknown').astype(str).tolist()
        else:
            # Erstelle synthetische Labels basierend auf Problemkategorien
            labels = self._create_synthetic_labels(texts)
        
        return texts, labels
    
    def _create_synthetic_labels(self, texts: List[str]) -> List[str]:
        """
        Erstellt synthetische Labels basierend auf Textinhalt.
        
        Args:
            texts: Liste von Texten
            
        Returns:
            Liste von Labels
        """
        labels = []
        
        # Definiere Kategorien basierend auf Keywords
        categories = {
            'engine_failure': ['failure', 'malfunction', 'shutdown', 'flameout'],
            'engine_warning': ['warning', 'caution', 'alert', 'indication'],
            'maintenance': ['maintenance', 'inspection', 'repair', 'replace'],
            'performance': ['performance', 'power', 'thrust', 'rpm', 'egt'],
            'other': []
        }
        
        for text in texts:
            text_lower = text.lower()
            assigned = False
            
            for category, keywords in categories.items():
                if category == 'other':
                    continue
                    
                if any(keyword in text_lower for keyword in keywords):
                    labels.append(category)
                    assigned = True
                    break
            
            if not assigned:
                labels.append('other')
        
        return labels
    
    def run_tfidf_svm(self, texts: List[str], labels: List[str]) -> Dict[str, Any]:
        """
        Führt TF-IDF + SVM Klassifikation durch.
        
        Args:
            texts: Liste von Texten
            labels: Liste von Labels
            
        Returns:
            Dictionary mit Ergebnissen
        """
        try:
            # Überprüfe Klassenverteilung
            label_counts = pd.Series(labels).value_counts()
            min_class_size = label_counts.min()
            
            # Wenn zu wenige Daten für stratifizierte Aufteilung, verwende einfache Aufteilung
            if min_class_size < 2 or len(texts) < 10:
                # Für sehr kleine Datensätze: verwende alle Daten für Training und Testing
                if len(texts) < 5:
                    X_train, X_test = texts, texts
                    y_train, y_test = labels, labels
                    self.logger.warning(f"Sehr kleiner Datensatz ({len(texts)} Samples). Verwende alle Daten für Training und Testing.")
                else:
                    # Einfache Aufteilung ohne Stratifikation
                    X_train, X_test, y_train, y_test = train_test_split(
                        texts, labels, test_size=0.2, random_state=42
                    )
                    self.logger.warning(f"Kleine Klassengrößen (min: {min_class_size}). Verwende einfache Aufteilung ohne Stratifikation.")
            else:
                # Normale stratifizierte Aufteilung
                X_train, X_test, y_train, y_test = train_test_split(
                    texts, labels, test_size=0.2, random_state=42, stratify=labels
                )
            
            # TF-IDF Vektorisierung
            vectorizer = self.models['tfidf_svm']['vectorizer']
            X_train_tfidf = vectorizer.fit_transform(X_train)
            X_test_tfidf = vectorizer.transform(X_test)
            
            # SVM Training
            classifier = self.models['tfidf_svm']['classifier']
            classifier.fit(X_train_tfidf, y_train)
            
            # Vorhersagen
            y_pred = classifier.predict(X_test_tfidf)
            
            # Metriken berechnen
            accuracy = accuracy_score(y_test, y_pred)
            
            # Für sehr kleine Datensätze: verwende zero_division Parameter
            try:
                report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            except:
                report = {"accuracy": accuracy}
            
            try:
                conf_matrix = confusion_matrix(y_test, y_pred)
            except:
                conf_matrix = np.array([[1]])
            
            # Feature Importance (Top TF-IDF Features)
            feature_names = vectorizer.get_feature_names_out()
            feature_importance = np.abs(classifier.coef_[0]) if hasattr(classifier, 'coef_') else None
            
            top_features = []
            if feature_importance is not None:
                top_indices = np.argsort(feature_importance)[-20:]
                top_features = [(feature_names[i], float(feature_importance[i])) for i in top_indices]
            
            return {
                'model_name': 'TF-IDF + SVM',
                'accuracy': float(accuracy),
                'classification_report': report,
                'confusion_matrix': conf_matrix.tolist(),
                'top_features': top_features,
                'predictions': list(zip(X_test, y_test, y_pred))[:10],  # Erste 10 Beispiele
                'data_info': {
                    'train_size': len(X_train),
                    'test_size': len(X_test),
                    'unique_labels': len(set(labels)),
                    'label_distribution': label_counts.to_dict()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei TF-IDF + SVM: {e}")
            return {'error': str(e)}
    
    def run_lda_analysis(self, texts: List[str], num_topics: int = 5) -> Dict[str, Any]:
        """
        Führt LDA Topic Modeling durch.
        
        Args:
            texts: Liste von Texten
            num_topics: Anzahl der Topics
            
        Returns:
            Dictionary mit Ergebnissen
        """
        if not GENSIM_AVAILABLE:
            return {'error': 'Gensim nicht verfügbar'}
        
        try:
            # Text preprocessing für LDA
            processed_texts = []
            for text in texts:
                # Einfache Tokenisierung
                tokens = text.lower().split()
                # Entferne sehr kurze Wörter
                tokens = [token for token in tokens if len(token) > 2]
                processed_texts.append(tokens)
            
            # Dictionary und Corpus erstellen
            dictionary = corpora.Dictionary(processed_texts)
            dictionary.filter_extremes(no_below=2, no_above=0.8)
            corpus = [dictionary.doc2bow(text) for text in processed_texts]
            
            # LDA Modell trainieren
            lda_model = LdaModel(
                corpus=corpus,
                id2word=dictionary,
                num_topics=num_topics,
                random_state=42,
                passes=10,
                alpha='auto',
                per_word_topics=True
            )
            
            # Topics extrahieren
            topics = []
            for idx, topic in lda_model.print_topics(-1):
                topics.append({
                    'topic_id': idx,
                    'words': topic
                })
            
            # Coherence Score (vereinfacht)
            coherence_score = 0.0  # Placeholder
            
            return {
                'model_name': 'Latent Dirichlet Allocation',
                'num_topics': num_topics,
                'topics': topics,
                'coherence_score': coherence_score,
                'perplexity': lda_model.log_perplexity(corpus)
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei LDA: {e}")
            return {'error': str(e)}
    
    def run_keybert_analysis(self, texts: List[str], top_k: int = 10) -> Dict[str, Any]:
        """
        Führt KeyBERT Keyword-Extraktion durch.
        
        Args:
            texts: Liste von Texten
            top_k: Anzahl der Top-Keywords
            
        Returns:
            Dictionary mit Ergebnissen
        """
        if 'keybert' not in self.models:
            return {'error': 'KeyBERT nicht verfügbar'}
        
        try:
            keybert_model = self.models['keybert']['model']
            
            # Keywords für alle Texte extrahieren
            all_keywords = []
            keyword_freq = {}
            
            for text in texts[:100]:  # Limitiere auf erste 100 Texte für Performance
                if len(text.strip()) > 10:  # Nur nicht-leere Texte
                    keywords = keybert_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), 
                                                            stop_words='english', top_k=top_k)
                    
                    for keyword, score in keywords:
                        all_keywords.append((keyword, score))
                        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
            
            # Top Keywords nach Häufigkeit
            top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            # Durchschnittliche Scores berechnen
            keyword_scores = {}
            for keyword, score in all_keywords:
                if keyword not in keyword_scores:
                    keyword_scores[keyword] = []
                keyword_scores[keyword].append(score)
            
            avg_keyword_scores = {k: np.mean(v) for k, v in keyword_scores.items()}
            top_scored_keywords = sorted(avg_keyword_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            return {
                'model_name': 'KeyBERT',
                'top_keywords_by_frequency': top_keywords,
                'top_keywords_by_score': top_scored_keywords,
                'total_keywords_extracted': len(all_keywords),
                'unique_keywords': len(keyword_freq)
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei KeyBERT: {e}")
            return {'error': str(e)}
    
    def run_distilbert_analysis(self, texts: List[str]) -> Dict[str, Any]:
        """
        Führt DistilBERT Sentiment-Analyse durch.
        
        Args:
            texts: Liste von Texten
            
        Returns:
            Dictionary mit Ergebnissen
        """
        if 'distilbert' not in self.models:
            return {'error': 'DistilBERT nicht verfügbar'}
        
        try:
            distilbert_model = self.models['distilbert']['model']
            
            # Sentiment-Analyse für Texte (limitiert für Performance)
            sentiments = []
            for text in texts[:100]:  # Limitiere auf erste 100 Texte
                if len(text.strip()) > 10:
                    result = distilbert_model(text[:512])  # Limitiere Textlänge
                    sentiments.append(result[0])
            
            # Sentiment-Verteilung
            sentiment_counts = {}
            confidence_scores = []
            
            for sentiment in sentiments:
                label = sentiment['label']
                score = sentiment['score']
                
                sentiment_counts[label] = sentiment_counts.get(label, 0) + 1
                confidence_scores.append(score)
            
            return {
                'model_name': 'DistilBERT Sentiment Analysis',
                'sentiment_distribution': sentiment_counts,
                'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
                'total_analyzed': len(sentiments),
                'sample_results': sentiments[:10]
            }
            
        except Exception as e:
            self.logger.error(f"Fehler bei DistilBERT: {e}")
            return {'error': str(e)}
    
    def compare_models(self, df: pd.DataFrame, text_column: str, 
                      target_column: str = None) -> Dict[str, Any]:
        """
        Vergleicht alle verfügbaren Modelle.
        
        Args:
            df: Input DataFrame
            text_column: Name der Textspalte
            target_column: Name der Zielspalte
            
        Returns:
            Dictionary mit Vergleichsergebnissen
        """
        self.logger.info("Starte Modellvergleich")
        
        # Daten vorbereiten
        texts, labels = self.prepare_classification_data(df, text_column, target_column)
        
        results = {
            'data_info': {
                'total_samples': len(texts),
                'unique_labels': len(set(labels)),
                'label_distribution': {label: labels.count(label) for label in set(labels)}
            },
            'model_results': {}
        }
        
        # TF-IDF + SVM
        if 'tfidf_svm' in self.models:
            self.logger.info("Führe TF-IDF + SVM durch")
            results['model_results']['tfidf_svm'] = self.run_tfidf_svm(texts, labels)
        
        # LDA
        if 'lda' in self.models:
            self.logger.info("Führe LDA durch")
            results['model_results']['lda'] = self.run_lda_analysis(texts)
        
        # KeyBERT
        if 'keybert' in self.models:
            self.logger.info("Führe KeyBERT durch")
            results['model_results']['keybert'] = self.run_keybert_analysis(texts)
        
        # DistilBERT
        if 'distilbert' in self.models:
            self.logger.info("Führe DistilBERT durch")
            results['model_results']['distilbert'] = self.run_distilbert_analysis(texts)
        
        # Modellvergleich-Zusammenfassung
        results['comparison_summary'] = self._create_comparison_summary(results['model_results'])
        
        self.logger.info("Modellvergleich abgeschlossen")
        return results
    
    def _create_comparison_summary(self, model_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt eine Zusammenfassung des Modellvergleichs.
        
        Args:
            model_results: Ergebnisse aller Modelle
            
        Returns:
            Zusammenfassung des Vergleichs
        """
        summary = {
            'models_compared': list(model_results.keys()),
            'best_accuracy': None,
            'recommendations': []
        }
        
        # Beste Genauigkeit finden
        accuracies = {}
        for model_name, results in model_results.items():
            if 'accuracy' in results:
                accuracies[model_name] = results['accuracy']
        
        if accuracies:
            best_model = max(accuracies, key=accuracies.get)
            summary['best_accuracy'] = {
                'model': best_model,
                'accuracy': accuracies[best_model]
            }
        
        # Empfehlungen basierend auf Ergebnissen
        if 'tfidf_svm' in model_results and 'accuracy' in model_results['tfidf_svm']:
            acc = model_results['tfidf_svm']['accuracy']
            if acc > 0.8:
                summary['recommendations'].append("TF-IDF + SVM zeigt hohe Genauigkeit für Klassifikation")
            elif acc < 0.6:
                summary['recommendations'].append("TF-IDF + SVM benötigt möglicherweise mehr Daten oder Feature-Engineering")
        
        if 'keybert' in model_results:
            summary['recommendations'].append("KeyBERT eignet sich gut für Keyword-Extraktion und Themenidentifikation")
        
        if 'lda' in model_results:
            summary['recommendations'].append("LDA kann für unüberwachte Themenmodellierung verwendet werden")
        
        return summary

