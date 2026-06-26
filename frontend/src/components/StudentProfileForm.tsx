import React, { useState, useEffect } from 'react';
import { useOptionEntryStore } from '@/store/optionEntry';
import { kcetAPI } from '@/services/api';

interface StudentProfileFormProps {
  onSubmit: (profile: any) => void;
  isLoading?: boolean;
}

export const StudentProfileForm: React.FC<StudentProfileFormProps> = ({ onSubmit, isLoading = false }) => {
  const [rank, setRank] = useState<string>('');
  const [category, setCategory] = useState<string>('GM');
  const [categories, setCategories] = useState<string[]>([]);
  const [courses, setCourses] = useState<any[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [error, setError] = useState<string>('');
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);
  const [selectedCourses, setSelectedCourses] = useState<string[]>([]);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);

  const setStudentProfile = useOptionEntryStore((state) => state.setStudentProfile);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const catResponse = await kcetAPI.getCategories();
        setCategories(catResponse.categories || []);
        
        const courseResponse = await kcetAPI.getCourses();
        setCourses(courseResponse.courses || []);

        const locResponse = await kcetAPI.getLocations();
        setLocations(locResponse.locations || []);
      } catch (err) {
        console.error('Error fetching data:', err);
      }
    };
    fetchData();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!rank || parseInt(rank) <= 0) {
      setError('Please enter a valid rank');
      return;
    }

    const profile = {
      rank: parseInt(rank),
      category,
      preferred_locations: selectedLocations.length > 0 ? selectedLocations : undefined,
      preferred_courses: selectedCourses.length > 0 ? selectedCourses : undefined,
    };

    setStudentProfile(profile);
    onSubmit(profile);
  };

  const handleCourseToggle = (courseCode: string) => {
    setSelectedCourses((prev) =>
      prev.includes(courseCode) ? prev.filter((c) => c !== courseCode) : [...prev, courseCode]
    );
  };

  const handleSelectAllLocations = () => {
    setSelectedLocations([...locations]);
  };

  const handleClearAllLocations = () => {
    setSelectedLocations([]);
  };

  const toggleLocationSelection = (location: string) => {
    setSelectedLocations((prev) =>
      prev.includes(location)
        ? prev.filter((l) => l !== location)
        : [...prev, location]
    );
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-8 max-w-2xl">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Student Profile</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Rank Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Rank <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            value={rank}
            onChange={(e) => setRank(e.target.value)}
            placeholder="Enter your KCET rank"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <p className="text-xs text-gray-500 mt-1">Your official KCET score-based rank</p>
        </div>

        {/* Category Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 mt-1">GM: General Merit, 2AR: 2A Reserved, etc.</p>
        </div>

        {/* Course Preferences */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Courses (Optional)
          </label>
          <div className="grid grid-cols-2 gap-3">
            {courses.map((course: any) => (
              <label key={course.course_code} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedCourses.includes(course.course_code)}
                  onChange={() => handleCourseToggle(course.course_code)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  disabled={isLoading}
                />
                <span className="text-sm text-gray-700">{course.course_code} - {course.course_name}</span>
              </label>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-2">Leave empty to see options from all courses</p>
        </div>

        {/* Location Preferences */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Locations (Optional)
          </label>
          
          {/* Dropdown Button */}
          <div className="relative mb-4">
            <button
              type="button"
              onClick={() => setShowLocationDropdown(!showLocationDropdown)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-left flex justify-between items-center hover:border-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
              disabled={isLoading}
            >
              <span className="text-gray-700">
                {selectedLocations.length === 0
                  ? 'Select locations in Karnataka'
                  : selectedLocations.length === locations.length
                  ? 'All locations selected'
                  : `${selectedLocations.length} location${selectedLocations.length !== 1 ? 's' : ''} selected`}
              </span>
              <span className={`transform transition-transform ${showLocationDropdown ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>

            {/* Dropdown Menu */}
            {showLocationDropdown && (
              <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                {/* Quick Actions */}
                <div className="p-3 border-b border-gray-200 flex gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      handleSelectAllLocations();
                    }}
                    className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 text-white rounded font-medium transition"
                    disabled={isLoading}
                  >
                    All
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      handleClearAllLocations();
                    }}
                    className="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 text-white rounded font-medium transition"
                    disabled={isLoading}
                  >
                    Clear
                  </button>
                </div>

                {/* Location List */}
                <div className="max-h-64 overflow-y-auto p-2">
                  {locations.map((location) => (
                    <label
                      key={location}
                      className="flex items-center space-x-3 px-3 py-2 hover:bg-blue-50 cursor-pointer rounded transition"
                    >
                      <input
                        type="checkbox"
                        checked={selectedLocations.includes(location)}
                        onChange={() => toggleLocationSelection(location)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        disabled={isLoading}
                      />
                      <span className="text-sm text-gray-700">{location}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Selected locations display */}
          {selectedLocations.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {selectedLocations.map((location) => (
                <span
                  key={location}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full flex items-center gap-2"
                >
                  {location}
                  <button
                    type="button"
                    onClick={() => toggleLocationSelection(location)}
                    className="hover:text-blue-600"
                  >
                    ✕
                  </button>
                </span>
              ))}
            </div>
          )}

          <p className="text-xs text-gray-500">
            Leave empty to see options from all locations across Karnataka
          </p>
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full mt-8 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
      >
        {isLoading ? 'Generating Predictions...' : 'Generate Predictions'}
      </button>
    </form>
  );
};

export default StudentProfileForm;
