"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import Image from "next/image"
import { Loader2, Upload, RefreshCw, BarChart, ImageIcon } from 'lucide-react'

// Import Recharts components for the chart
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

interface DataInsights {
  class_distribution: { [key: string]: number }
  sample_images: { [key: string]: string[] }
  image_dimensions: {
    min_width: number
    max_width: number
    avg_width: number
    min_height: number
    max_height: number
    avg_height: number
    total_images: number
  }
}

export default function MLPipelinePage() {
  const [predictionFile, setPredictionFile] = useState<File | null>(null)
  const [predictionResult, setPredictionResult] = useState<any>(null)
  const [predictLoading, setPredictLoading] = useState(false)
  const [retrainFile, setRetrainFile] = useState<File | null>(null)
  const [retrainResult, setRetrainResult] = useState<any>(null)
  const [retrainLoading, setRetrainLoading] = useState(false)
  const [predictionError, setPredictionError] = useState<string | null>(null)
  const [retrainError, setRetrainError] = useState<string | null>(null)
  const [dataInsights, setDataInsights] = useState<DataInsights | null>(null)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [insightsError, setInsightsError] = useState<string | null>(null)

  const API_BASE_URL = "http://localhost:5000" // Define API base URL

  // Fetch data insights on component mount
  useEffect(() => {
    const fetchInsights = async () => {
      try {
        setInsightsLoading(true)
        const response = await fetch(`${API_BASE_URL}/data-insights`)
        if (!response.ok) {
          throw new Error("Failed to fetch data insights.")
        }
        const data: DataInsights = await response.json()
        setDataInsights(data)
      } catch (error: any) {
        setInsightsError(error.message || "An error occurred while loading insights.")
      } finally {
        setInsightsLoading(false)
      }
    }
    fetchInsights()
  }, [])

  const handlePredictionFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setPredictionFile(event.target.files[0])
      setPredictionResult(null)
      setPredictionError(null)
    }
  }

  const handlePredict = async () => {
    if (!predictionFile) {
      setPredictionError("Please select an image file for prediction.")
      return
    }

    setPredictLoading(true)
    setPredictionResult(null)
    setPredictionError(null)

    const formData = new FormData()
    formData.append("file", predictionFile)

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Prediction failed")
      }

      const data = await response.json()
      setPredictionResult(data)
    } catch (error: any) {
      setPredictionError(error.message || "An unexpected error occurred during prediction.")
    } finally {
      setPredictLoading(false)
    }
  }

  const handleRetrainFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setRetrainFile(event.target.files[0])
      setRetrainResult(null)
      setRetrainError(null)
    }
  }

  const handleRetrain = async () => {
    if (!retrainFile) {
      setRetrainError("Please select a ZIP file containing new training data.")
      return
    }

    setRetrainLoading(true)
    setRetrainResult(null)
    setRetrainError(null)

    const formData = new FormData()
    formData.append("data_zip", retrainFile)

    try {
      const response = await fetch(`${API_BASE_URL}/retrain`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Retraining failed")
      }

      const data = await response.json()
      setRetrainResult(data)
      // Re-fetch insights after successful retraining
      const insightsResponse = await fetch(`${API_BASE_URL}/data-insights`)
      if (insightsResponse.ok) {
        const newInsights: DataInsights = await insightsResponse.json()
        setDataInsights(newInsights)
      }
    } catch (error: any) {
      setRetrainError(error.message || "An unexpected error occurred during retraining.")
    } finally {
      setRetrainLoading(false)
    }
  }

  // Transform class distribution data for the chart
  const chartData = dataInsights?.class_distribution
    ? Object.entries(dataInsights.class_distribution).map(([name, count]) => ({
        name,
        count,
      }))
    : []

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <main className="container mx-auto max-w-4xl space-y-8">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-10">ML Pipeline Dashboard</h1>

        {/* Model Prediction Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-6 w-6" /> Model Prediction
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">Upload an image to get a real-time prediction from the deployed model.</p>
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="prediction-image">Upload Image</Label>
              <Input id="prediction-image" type="file" accept="image/*" onChange={handlePredictionFileChange} />
            </div>
            {predictionFile && (
              <div className="mt-2">
                <p className="text-sm text-gray-500">Selected file: {predictionFile.name}</p>
                <Image
                  src={URL.createObjectURL(predictionFile) || "/placeholder.svg"}
                  alt="Preview"
                  width={150}
                  height={150}
                  className="mt-2 rounded-md object-cover"
                />
              </div>
            )}
            <Button onClick={handlePredict} disabled={predictLoading || !predictionFile}>
              {predictLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Predicting...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" /> Predict
                </>
              )}
            </Button>
            {predictionError && <p className="text-red-500 text-sm mt-2">{predictionError}</p>}
            {predictionResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <h3 className="font-semibold text-lg text-green-700">Prediction Result:</h3>
                <p>
                  <strong>Predicted Class:</strong> {predictionResult.predicted_class}
                </p>
                <p>
                  <strong>Confidence:</strong> {(predictionResult.confidence * 100).toFixed(2)}%
                </p>
                <p className="text-sm text-gray-600">Raw Output: {JSON.stringify(predictionResult.raw_predictions)}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Model Retraining Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="h-6 w-6" /> Model Retraining
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              Upload a ZIP file containing new image data (structured with class subdirectories) to trigger model
              retraining.
            </p>
            <div className="grid w-full max-w-sm items-center gap-1.5">
              <Label htmlFor="retrain-data">Upload New Data (ZIP)</Label>
              <Input id="retrain-data" type="file" accept=".zip" onChange={handleRetrainFileChange} />
            </div>
            {retrainFile && <p className="mt-2 text-sm text-gray-500">Selected file: {retrainFile.name}</p>}
            <Button onClick={handleRetrain} disabled={retrainLoading || !retrainFile}>
              {retrainLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Retraining...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" /> Trigger Retrain
                </>
              )}
            </Button>
            {retrainError && <p className="text-red-500 text-sm mt-2">{retrainError}</p>}
            {retrainResult && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
                <h3 className="font-semibold text-lg text-blue-700">Retraining Status:</h3>
                <p>{retrainResult.message}</p>
                {retrainResult.new_classes && (
                  <p className="text-sm text-gray-600">Detected classes: {retrainResult.new_classes.join(", ")}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Data Visualizations Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart className="h-6 w-6" /> Data Visualizations & Interpretations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {insightsLoading && <p className="text-gray-500">Loading data insights...</p>}
            {insightsError && <p className="text-red-500">{insightsError}</p>}
            {dataInsights && (
              <>
                <p className="text-gray-600">
                  This section displays insights from your dataset, helping you understand its characteristics.
                </p>
                <ul className="list-disc list-inside space-y-2 text-gray-700">
                  <li>
                    <strong>Feature 1: Class Distribution:</strong>
                    <p className="text-sm text-gray-500 italic">
                      Interpretation: This tells you if your dataset is balanced or imbalanced. An imbalanced dataset
                      might lead to the model performing well on the majority class but poorly on minority classes.
                    </p>
                    <div className="mt-2 p-4 bg-gray-100 rounded-md">
                      {chartData.length > 0 ? (
                        <ChartContainer
                          config={{
                            count: {
                              label: "Number of Images",
                              color: "hsl(142.1 76.2% 36.3%)", // Changed to a direct HSL value for visibility
                            },
                          }}
                          className="min-h-[200px] w-full"
                        >
                          <ResponsiveContainer width="100%" height="100%">
                            <RechartsBarChart data={chartData}>
                              <XAxis
                                dataKey="name"
                                tickLine={false}
                                axisLine={false}
                                tickMargin={8}
                                className="text-xs"
                              />
                              <YAxis tickLine={false} axisLine={false} tickMargin={8} className="text-xs" />
                              <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                              <Bar dataKey="count" fill="var(--color-count)" radius={8} />
                            </RechartsBarChart>
                          </ResponsiveContainer>
                        </ChartContainer>
                      ) : (
                        <p className="text-gray-500">No class distribution data available. Run `setup_data.py`.</p>
                      )}
                    </div>
                  </li>
                  <li>
                    <strong>Feature 2: Sample Images per Class:</strong>
                    <p className="text-sm text-gray-500 italic">
                      Interpretation: This helps you understand the visual characteristics of each class and identify
                      potential challenges (e.g., similar-looking classes, variations within a class).
                    </p>
                    <div className="mt-2 p-4 bg-gray-100 rounded-md grid grid-cols-3 gap-4">
                      {Object.keys(dataInsights.sample_images).length > 0 ? (
                        Object.entries(dataInsights.sample_images).map(([className, paths]: [string, string[]]) => (
                          <div key={className} className="col-span-3">
                            <h4 className="font-semibold text-md mb-2">{className} Samples:</h4>
                            <div className="grid grid-cols-3 gap-2">
                              {paths.map((path, index) => (
                                <Image
                                  key={index}
                                  src={`${API_BASE_URL}/data-images/${path}`}
                                  alt={`${className} sample ${index + 1}`}
                                  width={100}
                                  height={100}
                                  className="rounded-md object-cover"
                                  onError={(e) => {
                                    console.error(`Error loading image: ${e.currentTarget.src}`)
                                    e.currentTarget.src = "/placeholder.svg" // Fallback to placeholder
                                  }}
                                />
                              ))}
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="col-span-3 text-gray-500">No sample images available. Run `setup_data.py`.</p>
                      )}
                    </div>
                  </li>
                  <li>
                    <strong>Feature 3: Image Dimensions/Resolution:</strong>
                    <p className="text-sm text-gray-500 italic">
                      Interpretation: Understanding the original image sizes can inform your preprocessing strategy
                      (e.g., choosing an appropriate `target_size` for resizing). Very diverse sizes might indicate a
                      need for more robust resizing or cropping.
                    </p>
                    <div className="mt-2 p-4 bg-gray-100 rounded-md">
                      {dataInsights.image_dimensions.total_images > 0 ? (
                        <>
                          <p>
                            <strong>Total Images Analyzed:</strong> {dataInsights.image_dimensions.total_images}
                          </p>
                          <p>
                            <strong>Width:</strong> Min {dataInsights.image_dimensions.min_width}px, Max{" "}
                            {dataInsights.image_dimensions.max_width}px, Avg{" "}
                            {dataInsights.image_dimensions.avg_width.toFixed(2)}px
                          </p>
                          <p>
                            <strong>Height:</strong> Min {dataInsights.image_dimensions.min_height}px, Max{" "}
                            {dataInsights.image_dimensions.max_height}px, Avg{" "}
                            {dataInsights.image_dimensions.avg_height.toFixed(2)}px
                          </p>
                        </>
                      ) : (
                        <p className="text-gray-500">No image dimension data available. Run `setup_data.py`.</p>
                      )}
                    </div>
                  </li>
                </ul>
                <Textarea
                  placeholder="Add your detailed interpretations here based on your actual data visualizations."
                  rows={5}
                  className="mt-4"
                />
              </>
            )}
          </CardContent>
        </Card>

        {/* Model Up-time (Conceptual) */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Loader2 className="h-6 w-6" /> Model Up-time & Monitoring
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600">
              In a production environment, model up-time and performance are crucial. This section would typically
              integrate with monitoring tools.
            </p>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>
                <strong>API Status:</strong> <span className="font-semibold text-green-600">Online</span> (assuming your
                Flask API is running)
              </li>
              <li>
                <strong>Last Retrained:</strong>{" "}
                <span className="font-semibold text-gray-600">N/A (or date of last retraining)</span>
              </li>
              <li>
                <strong>Key Metrics (Conceptual):</strong>
                <ul className="list-disc list-inside ml-4 text-gray-600">
                  <li>Prediction Latency: Average time taken for a prediction request.</li>
                  <li>Error Rate: Percentage of failed prediction requests.</li>
                  <li>Model Drift: Monitoring changes in model performance over time with new data.</li>
                </ul>
              </li>
            </ul>
            <p className="text-sm text-gray-500 italic">
              Interpretation: Consistent monitoring ensures your model remains performant and available. High latency or
              error rates indicate issues that need immediate attention. Model drift detection helps determine when
              retraining is necessary.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
