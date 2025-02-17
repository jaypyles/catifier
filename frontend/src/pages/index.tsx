import React, { useEffect, useState } from "react";
import { Loader2, ImageIcon } from "lucide-react";
import { ImagesService } from "@/lib/services/images-service";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import useUser from "@/hooks/useUser";
import { toast } from "react-toastify";
import { useSession } from "next-auth/react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import Image from "next/image";
import LandingPage from "@/components/pages/landing-page";

export default function ImageGenerator() {
  const { user, updateUser } = useUser();
  const { data: session } = useSession();

  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentImage, setCurrentImage] = useState("");
  const [previousImages, setPreviousImages] = useState<string[]>([]);

  useEffect(() => {
    if (session) {
      ImagesService.getPreviousImages().then((images) => {
        setPreviousImages(images || []);
      });
    }
  }, [session]);

  if (!session) {
    return <LandingPage />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userPrompt = prompt.trim();

    setPrompt("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: userPrompt }),
      });

      if (response.status >= 400) {
        const data = await response.json();
        toast.error(data.error);
        return;
      }

      const data = await response.json();
      const newImage = data.image_url;

      updateUser({
        ...user,
        creditBalance: data.credits,
      });

      setCurrentImage(newImage);
      ImagesService.getPreviousImages().then((images) => {
        setPreviousImages(images || []);
      });
    } catch {
      toast.error("Error generating image");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-grow bg-gradient-to-r from-blue-100 to-purple-100">
      <div className="flex-grow flex flex-col items-center justify-center p-4">
        <h1 className="text-4xl font-bold mb-6 text-center text-black">
          Catifier
        </h1>
        <h2 className="text-xl font-bold mb-6 text-center text-black">
          Generate cat images with AI
        </h2>
        <form onSubmit={handleSubmit} className="w-full max-w-md mb-8">
          <div className="flex gap-2">
            <Input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter your image prompt"
              className="flex-grow"
              disabled={isLoading || user.creditBalance === 0}
            />
            <Button
              type="submit"
              disabled={isLoading || !prompt.trim() || user.creditBalance === 0}
            >
              Generate
            </Button>
          </div>
        </form>
        <div className="w-full max-w-2xl aspect-square bg-white rounded-lg shadow-lg flex items-center justify-center mb-8">
          {isLoading ? (
            <Loader2 className="w-16 h-16 animate-spin text-blue-500" />
          ) : currentImage ? (
            <Image
              src={currentImage}
              alt="Generated image"
              className="w-full h-full object-cover rounded-lg"
              width={512}
              height={512}
            />
          ) : (
            <ImageIcon className="w-16 h-16 text-gray-300" />
          )}
        </div>
        <div className="flex gap-4 justify-center">
          {previousImages.length > 0 && (
            <Carousel>
              <CarouselContent>
                {previousImages.map((img, index) => (
                  <CarouselItem key={index} className="w-48">
                    <Image
                      src={img}
                      onClick={() => {
                        setCurrentImage(img);
                      }}
                      alt={`Previous image ${index + 1}`}
                      className="w-full h-full rounded-lg"
                      width={512}
                      height={512}
                    />
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious className="text-black" />
              <CarouselNext className="text-black" />
            </Carousel>
          )}
        </div>
      </div>
      <div className="absolute inset-0 -z-10 h-full w-full bg-white bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem]">
        <div className="absolute bottom-0 left-0 right-0 top-0 bg-[radial-gradient(circle_500px_at_50%_200px,#C7D2FE,transparent)]"></div>
      </div>
    </div>
  );
}
