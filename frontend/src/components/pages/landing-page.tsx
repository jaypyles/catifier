import { Cat, Sparkles, Zap } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="h-full flex flex-col bg-gradient-to-r from-blue-100 to-purple-100">
      <main className="flex flex-col flex-grow">
        <section className="flex flex-col max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 text-center flex-grow items-center justify-center">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 mb-6">
            Generate Adorable Cat Images with AI
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Unleash your creativity with Catifier! Create unique, AI-generated
            cat images from your text descriptions. Perfect for cat lovers,
            artists, and anyone who needs a daily dose of feline cuteness.
          </p>
        </section>

        <section className="bg-white py-12 sm:py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
              How It Works
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="bg-blue-100 rounded-full p-4 inline-block mb-4">
                  <Zap className="h-8 w-8 text-blue-600" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-900">
                  1. Describe Your Cat
                </h4>
                <p className="text-gray-600">
                  Enter a detailed description of the cat you want to generate.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-purple-100 rounded-full p-4 inline-block mb-4">
                  <Sparkles className="h-8 w-8 text-purple-600" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-900">
                  2. AI Magic
                </h4>
                <p className="text-gray-600">
                  Our advanced AI processes your description and creates a
                  unique image.
                </p>
              </div>
              <div className="text-center">
                <div className="bg-green-100 rounded-full p-4 inline-block mb-4">
                  <Cat className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="text-xl font-semibold mb-2 text-gray-900">
                  3. Meet Your Cat
                </h4>
                <p className="text-gray-600">
                  Voilà! Your custom cat image is ready to download and share.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-blue-600 text-white py-12 sm:py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h3 className="text-3xl font-bold mb-6">
              Ready to Create Your Own Cat?
            </h3>
            <p className="text-xl mb-8 max-w-2xl mx-auto">
              Join Catifier today and start generating unique, AI-powered cat
              images that will make you smile!
            </p>
          </div>
        </section>
      </main>

      <div className="fixed inset-0 -z-10 h-full w-full bg-white bg-[linear-gradient(to_right,#f0f0f0_1px,transparent_1px),linear-gradient(to_bottom,#f0f0f0_1px,transparent_1px)] bg-[size:6rem_4rem]">
        <div className="absolute bottom-0 left-0 right-0 top-0 bg-[radial-gradient(circle_500px_at_50%_200px,#C7D2FE,transparent)]"></div>
      </div>
    </div>
  );
}
