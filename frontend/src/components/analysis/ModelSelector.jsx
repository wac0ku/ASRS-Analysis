import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Checkbox } from '@/components/ui/checkbox.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Play, CheckCircle, AlertCircle, Brain, BarChart3 } from 'lucide-react'

const API_BASE_URL = 'http://localhost:5002/api/asrs'

const ModelSelector = ({ sessionData, onAnalysisComplete }) => {
  const [selectedModels, setSelectedModels] = useState(['tfidf_svm'])
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [error, setError] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)

  const availableModels = [
    {
      id: 'tfidf_svm',
      name: 'TF-IDF + SVM',
      description: 'Term Frequency-Inverse Document Frequency mit Support Vector Machine für Textklassifikation',
      type: 'Klassifikation',
      available: true
    },
    {
      id: 'keybert',
      name: 'KeyBERT',
      description: 'BERT-basierte Keyword-Extraktion für die Identifikation wichtiger Begriffe',
      type: 'Keyword-Extraktion',
      available: false // Wird basierend auf Backend-Verfügbarkeit gesetzt
    },
    {
      id: 'lda',
      name: 'Latent Dirichlet Allocation',
      description: 'Unüberwachte Topic-Modellierung zur Entdeckung von Themen in Texten',
      type: 'Topic-Modelling',
      available: false
    },
    {
      id: 'distilbert',
      name: 'DistilBERT',
      description: 'Leichtgewichtiges BERT-Modell für Sentiment-Analyse und Textklassifikation',
      type: 'Sentiment-Analyse',
      available: false
    }
  ]

  const handleModelToggle = (modelId) => {
    setSelectedModels(prev => {
      if (prev.includes(modelId)) {
        return prev.filter(id => id !== modelId)
      } else {
        return [...prev, modelId]
      }
    })
  }

  const startAnalysis = async () => {
    if (selectedModels.length === 0) {
      setError('Bitte wählen Sie mindestens ein Modell aus.')
      return
    }

    setAnalyzing(true)
    setAnalysisProgress(0)
    setError(null)

    try {
      // Simuliere Progress
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => Math.min(prev + 5, 90))
      }, 500)

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionData.preprocessing.session_id,
          text_column: 'narrative',
          models: selectedModels
        }),
      })

      clearInterval(progressInterval)
      setAnalysisProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analyse fehlgeschlagen')
      }

      const result = await response.json()
      setAnalysisResult(result)
      
      // Erfolg an Parent-Komponente weiterleiten
      onAnalysisComplete(result)

    } catch (err) {
      setError(err.message)
    } finally {
      setAnalyzing(false)
    }
  }

  const getModelTypeColor = (type) => {
    switch (type) {
      case 'Klassifikation':
        return 'bg-blue-100 text-blue-800'
      case 'Keyword-Extraktion':
        return 'bg-green-100 text-green-800'
      case 'Topic-Modelling':
        return 'bg-purple-100 text-purple-800'
      case 'Sentiment-Analyse':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (!sessionData) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Bitte laden Sie zuerst eine ASRS-Datei hoch.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      {/* Session Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Datenübersicht</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="font-medium text-gray-500">Ursprüngliche Berichte</p>
              <p className="text-2xl font-bold text-blue-600">
                {sessionData.preprocessing.stats.original_count}
              </p>
            </div>
            <div>
              <p className="font-medium text-gray-500">Motorbezogene Berichte</p>
              <p className="text-2xl font-bold text-green-600">
                {sessionData.preprocessing.stats.filtered_count}
              </p>
            </div>
            <div>
              <p className="font-medium text-gray-500">Filterrate</p>
              <p className="text-2xl font-bold text-purple-600">
                {(sessionData.preprocessing.stats.filter_ratio * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="font-medium text-gray-500">Verarbeitete Spalten</p>
              <p className="text-2xl font-bold text-orange-600">
                {sessionData.preprocessing.processed_columns.length}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            NLP-Modell Auswahl
          </CardTitle>
          <CardDescription>
            Wählen Sie die Modelle aus, die für die Analyse verwendet werden sollen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {availableModels.map((model) => (
              <div
                key={model.id}
                className={`border rounded-lg p-4 transition-colors ${
                  selectedModels.includes(model.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${!model.available ? 'opacity-50' : ''}`}
              >
                <div className="flex items-start space-x-3">
                  <Checkbox
                    id={model.id}
                    checked={selectedModels.includes(model.id)}
                    onCheckedChange={() => handleModelToggle(model.id)}
                    disabled={!model.available || analyzing}
                  />
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <label
                        htmlFor={model.id}
                        className="text-sm font-medium cursor-pointer"
                      >
                        {model.name}
                      </label>
                      <Badge className={getModelTypeColor(model.type)}>
                        {model.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{model.description}</p>
                    {!model.available && (
                      <p className="text-xs text-red-600">
                        Modell nicht verfügbar (Dependencies fehlen)
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Progress */}
      {analyzing && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Analyse läuft...</span>
                <span className="text-sm text-gray-500">{analysisProgress}%</span>
              </div>
              <Progress value={analysisProgress} className="w-full" />
              <p className="text-xs text-gray-500">
                Die Modelle werden auf Ihre Daten angewendet. Dies kann einige Minuten dauern.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Analysis Result */}
      {analysisResult && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="space-y-2">
                <h3 className="font-medium text-green-700">Analyse abgeschlossen</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Analysierte Berichte:</strong> {analysisResult.results.data_info.total_samples}</p>
                  <p><strong>Verwendete Modelle:</strong> {Object.keys(analysisResult.results.model_results).length}</p>
                  <p><strong>Erkannte Kategorien:</strong> {analysisResult.results.data_info.unique_labels}</p>
                </div>
                <Button
                  onClick={() => setAnalysisResult(null)}
                  variant="outline"
                  size="sm"
                  className="mt-2"
                >
                  Neue Analyse starten
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Start Analysis Button */}
      {!analysisResult && !analyzing && (
        <div className="flex justify-center">
          <Button
            onClick={startAnalysis}
            disabled={selectedModels.length === 0 || analyzing}
            size="lg"
            className="px-8"
          >
            <Play className="w-4 h-4 mr-2" />
            Analyse starten
          </Button>
        </div>
      )}
    </div>
  )
}

export default ModelSelector

