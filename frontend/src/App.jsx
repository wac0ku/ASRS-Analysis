import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Upload, BarChart3, FileText, Settings } from 'lucide-react'
import ReportUploader from './components/upload/ReportUploader.jsx'
import Dashboard from './components/dashboard/Dashboard.jsx'
import ModelSelector from './components/analysis/ModelSelector.jsx'
import ResultsVisualization from './components/visualization/ResultsVisualization.jsx'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [sessionData, setSessionData] = useState(null)
  const [analysisResults, setAnalysisResults] = useState(null)

  const handleUploadSuccess = (data) => {
    setSessionData(data)
    setActiveTab('analysis')
  }

  const handleAnalysisComplete = (results) => {
    setAnalysisResults(results)
    setActiveTab('results')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ASRS Analysis Platform
          </h1>
          <p className="text-lg text-gray-600">
            Analyse von motorbezogenen Problemen in Aviation Safety Reports
          </p>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2" disabled={!sessionData}>
              <Settings className="w-4 h-4" />
              Analyse
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2" disabled={!analysisResults}>
              <BarChart3 className="w-4 h-4" />
              Ergebnisse
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="flex items-center gap-2" disabled={!analysisResults}>
              <FileText className="w-4 h-4" />
              Dashboard
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  ASRS-Daten hochladen
                </CardTitle>
                <CardDescription>
                  Laden Sie eine CSV-Datei mit ASRS-Berichten hoch, um die Analyse zu starten.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ReportUploader onUploadSuccess={handleUploadSuccess} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analysis" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Modellauswahl und Analyse
                </CardTitle>
                <CardDescription>
                  Wählen Sie die NLP-Modelle für die Analyse aus und starten Sie die Verarbeitung.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ModelSelector 
                  sessionData={sessionData} 
                  onAnalysisComplete={handleAnalysisComplete}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Analyseergebnisse
                </CardTitle>
                <CardDescription>
                  Visualisierung und Vergleich der NLP-Modell-Ergebnisse.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResultsVisualization analysisResults={analysisResults} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="dashboard" className="space-y-6">
            <Dashboard 
              sessionData={sessionData} 
              analysisResults={analysisResults} 
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

