'use client'

import { useState } from 'react'
import { Loader2, ImageIcon } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function ImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentImage, setCurrentImage] = useState('')
  const [previousImages, setPreviousImages] = useState<string[]>([])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Simulating image generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    const response = await fetch('/api/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    })

    const data = await response.json()
    console.log(`Data: ${data}`)
    const newImage = data.result
    setCurrentImage(newImage)
    setPreviousImages(prev => [newImage, ...prev.slice(0, 2)])
    setIsLoading(false)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-r from-blue-100 to-purple-100">
      <div className="flex-grow flex flex-col items-center justify-center p-4">
        <h1 className="text-4xl font-bold mb-6 text-center text-black">Catifier</h1>
        <h2 className="text-xl font-bold mb-6 text-center text-black">Generate cat images with AI</h2>
        <form onSubmit={handleSubmit} className="w-full max-w-md mb-8">
          <div className="flex gap-2">
            <Input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your image prompt"
              className="flex-grow"
            />
            <Button type="submit" disabled={isLoading}>Generate</Button>
          </div>
        </form>
        <div className="w-full max-w-2xl aspect-square bg-white rounded-lg shadow-lg flex items-center justify-center mb-8">
          {isLoading ? (
            <Loader2 className="w-16 h-16 animate-spin text-blue-500" />
          ) : currentImage ? (
            <img 
              src={currentImage} 
              alt="Generated image" 
              className="w-full h-full object-cover" 
            />
          ) : (
            <ImageIcon className="w-16 h-16 text-gray-300" />
          )}
        </div>
        <div className="flex gap-4 justify-center">
          {previousImages.map((img, index) => (
            <div key={index} className="w-24 h-24 bg-white rounded shadow-md flex items-center justify-center">
              <img 
                src={img} 
                alt={`Previous image ${index + 1}`} 
                className="w-full h-full object-cover" 
              />
            </div>
          ))}
        </div>
      </div>
      <div className="absolute inset-0 -z-10 h-full w-full bg-white bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem]">
        <div className="absolute bottom-0 left-0 right-0 top-0 bg-[radial-gradient(circle_500px_at_50%_200px,#C7D2FE,transparent)]"></div>
      </div>
    </div>
  )
}

