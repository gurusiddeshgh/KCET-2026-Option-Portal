import React from 'react';
import { ChoiceNode } from '@/services/api';
import { useOptionEntryStore } from '@/store/optionEntry';

interface PredictionResultsProps {
  choices: ChoiceNode[];
  totalMatches: number;
  dreamCount: number;
  targetCount: number;
  safetyCount: number;
}

const getChansingColor = (chancing: string) => {
  switch (chancing) {
    case 'High':
      return 'bg-green-100 text-green-800';
    case 'Medium':
      return 'bg-blue-100 text-blue-800';
    case 'Low':
      return 'bg-yellow-100 text-yellow-800';
    case 'Unlikely':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const PredictionResults: React.FC<PredictionResultsProps> = ({
  choices,
  totalMatches,
  dreamCount,
  targetCount,
  safetyCount,
}) => {
  const addChoice = useOptionEntryStore((state) => state.addChoice);
  const choices_list = useOptionEntryStore((state) => state.choices);

  const handleAddToList = (choice: ChoiceNode) => {
    addChoice({
      collegeCode: choice.college_code,
      courseCode: choice.course_code,
      collegeName: choice.college_name,
      courseName: choice.course_name,
      location: choice.location,
      chancing: choice.chancing,
    });
  };

  const isAlreadyAdded = (collegeCode: string, courseCode: string) => {
    return choices_list.some(
      (c) => c.collegeCode === collegeCode && c.courseCode === courseCode
    );
  };

  return (
    <div className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Prediction Results</h2>

        {/* Summary Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-green-50 border-l-4 border-green-600 p-4 rounded">
            <p className="text-sm text-gray-600">Dream Options</p>
            <p className="text-2xl font-bold text-green-600">{dreamCount}</p>
          </div>
          <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
            <p className="text-sm text-gray-600">Target Options</p>
            <p className="text-2xl font-bold text-blue-600">{targetCount}</p>
          </div>
          <div className="bg-yellow-50 border-l-4 border-yellow-600 p-4 rounded">
            <p className="text-sm text-gray-600">Safety Options</p>
            <p className="text-2xl font-bold text-yellow-600">{safetyCount}</p>
          </div>
          <div className="bg-purple-50 border-l-4 border-purple-600 p-4 rounded">
            <p className="text-sm text-gray-600">Total Matches</p>
            <p className="text-2xl font-bold text-purple-600">{totalMatches}</p>
          </div>
        </div>

        {/* Legend */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm font-semibold text-gray-700 mb-2">Probability Guide:</p>
          <div className="flex flex-wrap gap-3">
            <span className="inline-block">
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor('High')}`}>
                High
              </span>
              <span className="text-xs text-gray-600 ml-1">≤ 0.90 ratio</span>
            </span>
            <span className="inline-block">
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor('Medium')}`}>
                Medium
              </span>
              <span className="text-xs text-gray-600 ml-1">0.90-1.02 ratio</span>
            </span>
            <span className="inline-block">
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor('Low')}`}>
                Low
              </span>
              <span className="text-xs text-gray-600 ml-1">1.02-1.15 ratio</span>
            </span>
            <span className="inline-block">
              <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor('Unlikely')}`}>
                Unlikely
              </span>
              <span className="text-xs text-gray-600 ml-1">> 1.15 ratio</span>
            </span>
          </div>
        </div>
      </div>

      {/* Choices Table */}
      <div className="overflow-x-auto">
        <table className="w-full bg-white shadow-md rounded-lg overflow-hidden">
          <thead>
            <tr className="bg-gray-800 text-white">
              <th className="px-4 py-3 text-left text-sm font-semibold">#</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">College</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Course</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Location</th>
              <th className="px-4 py-3 text-center text-sm font-semibold">R1</th>
              <th className="px-4 py-3 text-center text-sm font-semibold">R2</th>
              <th className="px-4 py-3 text-center text-sm font-semibold">R3</th>
              <th className="px-4 py-3 text-center text-sm font-semibold">Action</th>
            </tr>
          </thead>
          <tbody>
            {choices.map((choice, index) => {
              const isAdded = isAlreadyAdded(choice.college_code, choice.course_code);
              return (
                <tr
                  key={`${choice.college_code}-${choice.course_code}-${index}`}
                  className="border-b hover:bg-gray-50 transition"
                >
                  <td className="px-4 py-3 text-sm text-gray-700">{choice.priority_number}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-800">
                    {choice.college_name}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{choice.course_name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{choice.location}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor(
                        choice.chancing.round_1
                      )}`}
                    >
                      {choice.chancing.round_1}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor(
                        choice.chancing.round_2
                      )}`}
                    >
                      {choice.chancing.round_2}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getChansingColor(
                        choice.chancing.round_3
                      )}`}
                    >
                      {choice.chancing.round_3}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => handleAddToList(choice)}
                      disabled={isAdded}
                      className={`px-3 py-1 rounded text-xs font-semibold transition ${
                        isAdded
                          ? 'bg-gray-200 text-gray-600 cursor-not-allowed'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {isAdded ? 'Added' : 'Add'}
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PredictionResults;
