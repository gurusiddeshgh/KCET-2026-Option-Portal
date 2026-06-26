'use client';

import React, { useState } from 'react';
import StudentProfileForm from '@/components/StudentProfileForm';
import PredictionResults from '@/components/PredictionResults';
import { kcetAPI } from '@/services/api';
import { useOptionEntryStore } from '@/store/optionEntry';

export default function PredictorPage() {
  const [predictions, setPredictions] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [showResults, setShowResults] = useState(false);

  const setTotalMatches = useOptionEntryStore((state) => state.setTotalMatches);
  const setDreamCount = useOptionEntryStore((state) => state.setDreamCount);
  const setTargetCount = useOptionEntryStore((state) => state.setTargetCount);
  const setSafetyCount = useOptionEntryStore((state) => state.setSafetyCount);
  const setChoices = useOptionEntryStore((state) => state.setChoices);

  const handlePredictionsGenerated = async (profile: any) => {
    setIsLoading(true);
    setError('');
    setShowResults(false);

    try {
      const response = await kcetAPI.predictColleges(profile);

      // Store in Zustand store
      setTotalMatches(response.total_matches);
      setDreamCount(response.dream_count);
      setTargetCount(response.target_count);
      setSafetyCount(response.safety_count);

      // Convert response format to store format
      const formattedChoices = response.choices.map((choice: any) => ({
        priorityNumber: choice.priority_number,
        collegeCode: choice.college_code,
        courseCode: choice.course_code,
        collegeName: choice.college_name,
        courseName: choice.course_name,
        location: choice.location,
        chancing: choice.chancing,
      }));

      setChoices(formattedChoices);
      setPredictions(response);
      setShowResults(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to generate predictions. Please try again.'
      );
      console.error('Prediction error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Form */}
        <div className="lg:col-span-1">
          <StudentProfileForm onSubmit={handlePredictionsGenerated} isLoading={isLoading} />
        </div>

        {/* Right Column - Results */}
        <div className="lg:col-span-2">
          {error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {isLoading && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <div className="inline-block">
                <div className="animate-spin">
                  <svg
                    className="w-12 h-12 text-blue-600"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                </div>
              </div>
              <p className="text-gray-600 mt-4 font-semibold">Generating predictions...</p>
              <p className="text-gray-500 text-sm">Analyzing cutoff data and applying Sandwich Strategy</p>
            </div>
          )}

          {showResults && predictions && (
            <PredictionResults
              choices={predictions.choices}
              totalMatches={predictions.total_matches}
              dreamCount={predictions.dream_count}
              targetCount={predictions.target_count}
              safetyCount={predictions.safety_count}
            />
          )}

          {!showResults && !isLoading && !error && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <p className="text-gray-500 text-lg">
                Enter your details to generate predictions
              </p>
              <p className="text-gray-400 text-sm mt-2">
                Your personalized choice list will appear here
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
