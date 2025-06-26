import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
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
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts'
import { BarChart3, PieChart as PieChartIcon, TrendingUp, AlertCircle, Target } from 'lucide-react'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

const ResultsVisualization = ({ analysisResults }) => {
  const [activeTab, setActiveTab] = useState('overview')

  if (!analysisResults) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Keine Analyseergebnisse verfügbar. Bitte führen Sie zuerst eine Analyse durch.
        </AlertDescription>
      </Alert>
    )
  }

  const { results } = analysisResults
  const modelResults = results.model_results || {}

  // Prepare accuracy comparison data
  const accuracyData = Object.entries(modelResults)
    .filter(([_, result]) => result.accuracy !== undefined)
    .map(([modelName, result]) => ({
      model: result.model_name || modelName,
      accuracy: (result.accuracy * 100).toFixed(1),
      accuracyValue: result.accuracy
    }))

  // Prepare label distribution data
  const labelDistribution = Object.entries(results.data_info.label_distribution || {})
    .map(([label, count]) => ({
      label: label.replace('_', ' ').toUpperCase(),
      count,
      percentage: ((count / results.data_info.total_samples) * 100).toFixed(1)
    }))

  // Prepare keyword data (from KeyBERT if available)
  const keywordData = modelResults.keybert?.top_keywords_by_frequency?.slice(0, 10).map(([keyword, frequency]) => ({
    keyword: keyword.length > 15 ? keyword.substring(0, 15) + '...' : keyword,
    frequency,
    fullKeyword: keyword
  })) || []

  // Prepare sentiment data (from DistilBERT if available)
  const sentimentData = modelResults.distilbert?.sentiment_distribution ? 
    Object.entries(modelResults.distilbert.sentiment_distribution).map(([sentiment, count]) => ({
      sentiment: sentiment.toUpperCase(),
      count,
      percentage: ((count / Object.values(modelResults.distilbert.sentiment_distribution).reduce((a, b) => a + b, 0)) * 100).toFixed(1)
    })) : []

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.dataKey}: {entry.value}
              {entry.dataKey === 'accuracy' && '%'}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Analysierte Berichte</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{results.data_info.total_samples}</div>
            <p className="text-xs text-muted-foreground">
              Motorbezogene ASRS-Berichte
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Verwendete Modelle</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Object.keys(modelResults).length}</div>
            <p className="text-xs text-muted-foreground">
              NLP-Modelle im Vergleich
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Erkannte Kategorien</CardTitle>
            <PieChartIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{results.data_info.unique_labels}</div>
            <p className="text-xs text-muted-foreground">
              Problemkategorien identifiziert
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Visualizations */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Übersicht</TabsTrigger>
          <TabsTrigger value="accuracy">Modellgenauigkeit</TabsTrigger>
          <TabsTrigger value="categories">Kategorien</TabsTrigger>
          <TabsTrigger value="keywords">Keywords</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Model Performance Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Modell-Performance</CardTitle>
                <CardDescription>Übersicht der verwendeten Modelle und ihrer Eigenschaften</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(modelResults).map(([modelName, result]) => (
                    <div key={modelName} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{result.model_name || modelName}</p>
                        <p className="text-sm text-gray-500">
                          {result.accuracy ? `Genauigkeit: ${(result.accuracy * 100).toFixed(1)}%` : 'Analyse-Modell'}
                        </p>
                      </div>
                      <Badge variant={result.accuracy ? 'default' : 'secondary'}>
                        {result.accuracy ? 'Klassifikation' : 'Analyse'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Label Distribution */}
            {labelDistribution.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Problemverteilung</CardTitle>
                  <CardDescription>Verteilung der erkannten Problemkategorien</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={labelDistribution}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ label, percentage }) => `${label}: ${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {labelDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="accuracy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Modellgenauigkeit Vergleich</CardTitle>
              <CardDescription>Vergleich der Klassifikationsgenauigkeit verschiedener Modelle</CardDescription>
            </CardHeader>
            <CardContent>
              {accuracyData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={accuracyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="accuracy" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Keine Genauigkeitsdaten verfügbar. Stellen Sie sicher, dass Klassifikationsmodelle verwendet wurden.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Detailed Model Results */}
          <div className="grid gap-4">
            {Object.entries(modelResults).map(([modelName, result]) => (
              <Card key={modelName}>
                <CardHeader>
                  <CardTitle className="text-lg">{result.model_name || modelName}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {result.accuracy && (
                      <div>
                        <p className="font-medium text-gray-500">Genauigkeit</p>
                        <p className="text-xl font-bold text-blue-600">
                          {(result.accuracy * 100).toFixed(1)}%
                        </p>
                      </div>
                    )}
                    {result.top_keywords && (
                      <div>
                        <p className="font-medium text-gray-500">Top Keywords</p>
                        <p className="text-xl font-bold text-green-600">
                          {result.top_keywords.length}
                        </p>
                      </div>
                    )}
                    {result.topics && (
                      <div>
                        <p className="font-medium text-gray-500">Topics</p>
                        <p className="text-xl font-bold text-purple-600">
                          {result.topics.length}
                        </p>
                      </div>
                    )}
                    {result.sentiment_distribution && (
                      <div>
                        <p className="font-medium text-gray-500">Sentiments</p>
                        <p className="text-xl font-bold text-orange-600">
                          {Object.keys(result.sentiment_distribution).length}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Problemkategorien</CardTitle>
              <CardDescription>Detaillierte Aufschlüsselung der erkannten Problemkategorien</CardDescription>
            </CardHeader>
            <CardContent>
              {labelDistribution.length > 0 ? (
                <div className="space-y-4">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={labelDistribution} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="label" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                  
                  <div className="grid gap-2">
                    {labelDistribution.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-2 border rounded">
                        <span className="font-medium">{item.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-500">{item.count} Berichte</span>
                          <Badge variant="outline">{item.percentage}%</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Keine Kategoriedaten verfügbar.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="keywords" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Wichtige Keywords</CardTitle>
              <CardDescription>Häufigste und relevanteste Begriffe in den Berichten</CardDescription>
            </CardHeader>
            <CardContent>
              {keywordData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={keywordData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="keyword" />
                    <YAxis />
                    <Tooltip 
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload
                          return (
                            <div className="bg-white p-3 border rounded-lg shadow-lg">
                              <p className="font-medium">{data.fullKeyword}</p>
                              <p>Häufigkeit: {data.frequency}</p>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Bar dataKey="frequency" fill="#ffc658" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    Keine Keyword-Daten verfügbar. KeyBERT-Modell wurde möglicherweise nicht verwendet.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default ResultsVisualization

