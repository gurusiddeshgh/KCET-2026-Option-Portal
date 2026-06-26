import React from 'react';
import { useOptionEntryStore } from '@/store/optionEntry';

export const ChoiceList: React.FC = () => {
  const choices = useOptionEntryStore((state) => state.choices);
  const removeChoice = useOptionEntryStore((state) => state.removeChoice);
  const reorderChoices = useOptionEntryStore((state) => state.reorderChoices);
  const clearList = useOptionEntryStore((state) => state.clearList);
  const studentProfile = useOptionEntryStore((state) => state.studentProfile);

  const handleDragStart = (e: React.DragEvent, index: number) => {
    e.dataTransfer?.setData('dragIndex', index.toString());
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, targetIndex: number) => {
    e.preventDefault();
    const dragIndex = parseInt(e.dataTransfer?.getData('dragIndex') || '-1');
    if (dragIndex !== -1 && dragIndex !== targetIndex) {
      reorderChoices(dragIndex, targetIndex);
    }
  };

  const handleExportCSV = () => {
    if (choices.length === 0) {
      alert('No choices to export');
      return;
    }

    const headers = [
      'Priority',
      'College Code',
      'College Name',
      'Course Code',
      'Course Name',
      'Location',
      'Round 1 Chancing',
      'Round 2 Chancing',
      'Round 3 Chancing',
    ];

    const rows = choices.map((choice) => [
      choice.priorityNumber,
      choice.collegeCode,
      choice.collegeName,
      choice.courseCode,
      choice.courseName,
      choice.location,
      choice.chancing.round_1,
      choice.chancing.round_2,
      choice.chancing.round_3,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `KCET_Choices_${new Date().toISOString().split('T')[0]}.csv`);
    link.click();
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">My Choice List ({choices.length}/100)</h2>
        <div className="flex space-x-2">
          <button
            onClick={handleExportCSV}
            disabled={choices.length === 0}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition"
          >
            Export CSV
          </button>
          <button
            onClick={clearList}
            disabled={choices.length === 0}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-semibold transition"
          >
            Clear All
          </button>
        </div>
      </div>

      {studentProfile && (
        <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-600 rounded">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Rank:</span> {studentProfile.rank} |{' '}
            <span className="font-semibold">Category:</span> {studentProfile.category}
          </p>
        </div>
      )}

      {choices.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No choices added yet</p>
          <p className="text-gray-400 text-sm">Go to Predictor to add colleges to your list</p>
        </div>
      ) : (
        <div className="space-y-2">
          {choices.map((choice, index) => (
            <div
              key={`${choice.collegeCode}-${choice.courseCode}`}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, index)}
              className="flex items-center p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 cursor-move transition"
            >
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-4">
                {choice.priorityNumber}
              </div>
              <div className="flex-grow">
                <p className="font-semibold text-gray-800">{choice.collegeName}</p>
                <p className="text-sm text-gray-600">
                  {choice.courseName} • {choice.location}
                </p>
              </div>
              <div className="flex space-x-2 text-xs">
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                  R1: {choice.chancing.round_1}
                </span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                  R2: {choice.chancing.round_2}
                </span>
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                  R3: {choice.chancing.round_3}
                </span>
              </div>
              <button
                onClick={() => removeChoice(choice.collegeCode, choice.courseCode)}
                className="ml-4 px-3 py-1 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChoiceList;
