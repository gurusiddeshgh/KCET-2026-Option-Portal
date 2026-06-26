export default function Home() {
  return (
    <div className="container mx-auto py-12">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Hero Section */}
        <div className="flex flex-col justify-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Smart College Predictions for KCET 2026
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Get intelligent college predictions based on your rank and category using our advanced algorithm that analyzes historical cutoff trends.
          </p>
          <ul className="space-y-3 mb-8">
            <li className="flex items-center text-gray-700">
              <span className="text-green-600 mr-3">✓</span> Analyze historical cutoff data from multiple rounds
            </li>
            <li className="flex items-center text-gray-700">
              <span className="text-green-600 mr-3">✓</span> Sandwich Strategy optimization for maximum safety
            </li>
            <li className="flex items-center text-gray-700">
              <span className="text-green-600 mr-3">✓</span> Drag-and-drop choice list management
            </li>
            <li className="flex items-center text-gray-700">
              <span className="text-green-600 mr-3">✓</span> Export to CSV for official KEA portal entry
            </li>
          </ul>
          <a
            href="/predictor"
            className="inline-block px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition w-fit"
          >
            Get Started
          </a>
        </div>

        {/* Info Section */}
        <div className="space-y-6">
          <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded">
            <h3 className="font-bold text-blue-900 mb-2">The Sandwich Strategy</h3>
            <p className="text-sm text-blue-800">
              Our algorithm distributes your 100 choices across three risk categories:
              20 Dream options, 50 Target options, and 30 Safety options for optimal coverage.
            </p>
          </div>

          <div className="bg-green-50 border-l-4 border-green-600 p-6 rounded">
            <h3 className="font-bold text-green-900 mb-2">Probability Assessment</h3>
            <p className="text-sm text-green-800">
              Each option is rated for probability across three rounds (High, Medium, Low, Unlikely)
              based on the variance ratio of your rank against historical cutoffs.
            </p>
          </div>

          <div className="bg-purple-50 border-l-4 border-purple-600 p-6 rounded">
            <h3 className="font-bold text-purple-900 mb-2">Real-Time Updates</h3>
            <p className="text-sm text-purple-800">
              Pre-loaded with 2025 cutoff data. Powered by a high-concurrency backend
              supporting massive traffic during option entry windows.
            </p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mt-16">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="font-bold text-gray-900 mb-2">Smart Predictions</h3>
            <p className="text-gray-600 text-sm">
              AI-powered algorithm analyzes historical trends to predict your chances at each college.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-4">🔄</div>
            <h3 className="font-bold text-gray-900 mb-2">Easy Customization</h3>
            <p className="text-gray-600 text-sm">
              Drag-and-drop interface to reorder and customize your choice list as needed.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="font-bold text-gray-900 mb-2">Data Export</h3>
            <p className="text-gray-600 text-sm">
              Export your finalized choices to CSV format for direct entry into KEA portal.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
