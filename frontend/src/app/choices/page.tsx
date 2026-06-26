'use client';

import ChoiceList from '@/components/ChoiceList';

export default function ChoicesPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Manage Your Choices</h1>
        <p className="text-gray-600">Organize and finalize your college choices for submission</p>
      </div>

      <ChoiceList />

      {/* Info Section */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded-lg">
          <h3 className="font-bold text-blue-900 mb-2">Tips for Choice List</h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• Start with high-probability options in the beginning</li>
            <li>• Mix dream, target, and safety options</li>
            <li>• Drag to reorder based on your preferences</li>
            <li>• Ensure you have at least 1-2 safety options</li>
            <li>• Review probabilities for each round</li>
          </ul>
        </div>

        <div className="bg-green-50 border-l-4 border-green-600 p-6 rounded-lg">
          <h3 className="font-bold text-green-900 mb-2">Before Submission</h3>
          <ul className="text-sm text-green-800 space-y-2">
            <li>✓ Verify all college codes and course names</li>
            <li>✓ Check location preferences are correct</li>
            <li>✓ Ensure up to 100 choices (or your target)</li>
            <li>✓ Export and review the CSV file</li>
            <li>✓ Submit during the official KEA window</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
