import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent } from '@/components/ui/card.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react'

const API_BASE_URL = 'http://localhost:5002/api/asrs'

const ReportUploader = ({ onUploadSuccess }) => {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState(null)
  const [preprocessing, setPreprocessing] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setError(null)
        setUploadResult(null)
      } else {
        setError('Bitte wählen Sie eine CSV-Datei aus.')
        setFile(null)
      }
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile) {
      if (droppedFile.type === 'text/csv' || droppedFile.name.endsWith('.csv')) {
        setFile(droppedFile)
        setError(null)
        setUploadResult(null)
      } else {
        setError('Bitte wählen Sie eine CSV-Datei aus.')
      }
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
  }

  const uploadFile = async () => {
    if (!file) return

    setUploading(true)
    setUploadProgress(0)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Simuliere Upload-Progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Upload fehlgeschlagen')
      }

      const result = await response.json()
      setUploadResult(result)

      // Automatisch Preprocessing starten
      await startPreprocessing(result.file_info.filepath)

    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const startPreprocessing = async (filepath) => {
    setPreprocessing(true)
    
    try {
      const response = await fetch(`${API_BASE_URL}/preprocess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filepath: filepath,
          text_columns: ['narrative', 'synopsis', 'problem_description']
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Preprocessing fehlgeschlagen')
      }

      const result = await response.json()
      
      // Erfolg an Parent-Komponente weiterleiten
      onUploadSuccess({
        ...uploadResult,
        preprocessing: result
      })

    } catch (err) {
      setError(`Preprocessing-Fehler: ${err.message}`)
    } finally {
      setPreprocessing(false)
    }
  }

  const resetUpload = () => {
    setFile(null)
    setUploadResult(null)
    setError(null)
    setUploadProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      {!uploadResult && (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            file ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-gray-400'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          <div className="flex flex-col items-center space-y-4">
            <div className={`p-3 rounded-full ${file ? 'bg-green-100' : 'bg-gray-100'}`}>
              {file ? (
                <CheckCircle className="w-8 h-8 text-green-600" />
              ) : (
                <Upload className="w-8 h-8 text-gray-600" />
              )}
            </div>
            
            {file ? (
              <div className="space-y-2">
                <p className="text-lg font-medium text-green-700">Datei ausgewählt</p>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <FileText className="w-4 h-4" />
                  <span>{file.name}</span>
                  <span>({formatFileSize(file.size)})</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetUpload}
                    className="h-6 w-6 p-0"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-700">
                  CSV-Datei hier ablegen oder auswählen
                </p>
                <p className="text-sm text-gray-500">
                  Unterstützte Formate: .csv
                </p>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
              disabled={uploading || preprocessing}
            >
              <Upload className="w-4 h-4 mr-2" />
              Datei auswählen
            </Button>
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {(uploading || preprocessing) && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {uploading ? 'Datei wird hochgeladen...' : 'Daten werden vorverarbeitet...'}
                </span>
                <span className="text-sm text-gray-500">
                  {uploading ? `${uploadProgress}%` : 'Verarbeitung läuft...'}
                </span>
              </div>
              <Progress value={uploading ? uploadProgress : undefined} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Result */}
      {uploadResult && !preprocessing && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
              <div className="space-y-2">
                <h3 className="font-medium text-green-700">Upload erfolgreich</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Datei:</strong> {uploadResult.file_info.filename}</p>
                  <p><strong>Zeilen:</strong> {uploadResult.file_info.rows}</p>
                  <p><strong>Spalten:</strong> {uploadResult.file_info.columns}</p>
                  <p><strong>Spalten:</strong> {uploadResult.file_info.column_names.join(', ')}</p>
                </div>
                <Button
                  onClick={resetUpload}
                  variant="outline"
                  size="sm"
                  className="mt-2"
                >
                  Neue Datei hochladen
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

      {/* Upload Button */}
      {file && !uploadResult && !uploading && (
        <div className="flex justify-center">
          <Button
            onClick={uploadFile}
            disabled={uploading || preprocessing}
            size="lg"
            className="px-8"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload starten
          </Button>
        </div>
      )}
    </div>
  )
}

export default ReportUploader

