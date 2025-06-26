import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  Download, 
  FileText, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Plane,
  AlertCircle
} from 'lucide-react'

const API_BASE_URL = 'http://localhost:5002/api/asrs'

const Dashboard = ({ sessionData, analysisResults }) => {
  const [generatingReport, setGeneratingReport] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [error, setError] = useState(null)

  if (!sessionData || !analysisResults) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Dashboard ist verfügbar, nachdem Upload und Analyse abgeschlossen sind.
        </AlertDescription>
      </Alert>
    )
  }

  const { preprocessing } = sessionData
  const { results } = analysisResults

  const generateReport = async () => {
    setGeneratingReport(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE_URL}/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: preprocessing.session_id
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Bericht-Generierung fehlgeschlagen')
      }

      const result = await response.json()
      setReportData(result.report)

    } catch (err) {
      setError(err.message)
    } finally {
      setGeneratingReport(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Gesamte Berichte</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{preprocessing.stats.original_count}</div>
            <p className="text-xs text-muted-foreground">
              Ursprünglich hochgeladen
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Motorbezogen</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {preprocessing.stats.filtered_count}
            </div>
            <p className="text-xs text-muted-foreground">
              {(preprocessing.stats.filter_ratio * 100).toFixed(1)}% der Berichte
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Modelle verwendet</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {Object.keys(results.model_results).length}
            </div>
            <p className="text-xs text-muted-foreground">
              NLP-Modelle analysiert
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kategorien</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {results.data_info.unique_labels}
            </div>
            <p className="text-xs text-muted-foreground">
              Problemkategorien erkannt
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Report Generation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Bericht generieren
          </CardTitle>
          <CardDescription>
            Erstellen Sie einen detaillierten Analysebericht für Ihre Professoren
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {!reportData ? (
              <Button 
                onClick={generateReport} 
                disabled={generatingReport}
                size="lg"
              >
                {generatingReport ? (
                  <>
                    <Clock className="w-4 h-4 mr-2 animate-spin" />
                    Bericht wird generiert...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4 mr-2" />
                    Bericht generieren
                  </>
                )}
              </Button>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <h3 className="font-medium text-green-800">Bericht erfolgreich generiert</h3>
                  </div>
                  <p className="text-sm text-green-700">
                    Der Analysebericht wurde erstellt und kann heruntergeladen werden.
                  </p>
                </div>
                
                <Button onClick={() => setReportData(null)} variant="outline">
                  Neuen Bericht generieren
                </Button>
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

