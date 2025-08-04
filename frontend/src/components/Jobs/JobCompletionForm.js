import React, { useState, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const JobCompletionForm = ({ job, onComplete }) => {
  const [beforeImage, setBeforeImage] = useState(null);
  const [afterImage, setAfterImage] = useState(null);
  const [beforePreview, setBeforePreview] = useState(null);
  const [afterPreview, setAfterPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const beforeInputRef = useRef(null);
  const afterInputRef = useRef(null);
  const { user } = useAuth();

  const handleImageCapture = (file, type) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (type === 'before') {
          setBeforeImage(file);
          setBeforePreview(e.target.result);
        } else {
          setAfterImage(file);
          setAfterPreview(e.target.result);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!beforeImage || !afterImage) {
      alert('❌ Please capture both before and after images.');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('before_image', beforeImage);
      formData.append('after_image', afterImage);

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/jobs/${job.id}/complete-work`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
          },
          body: formData
        }
      );

      if (response.ok) {
        const result = await response.json();
        alert(`✅ Job completed successfully! You earned R${result.payment_amount}`);
        onComplete && onComplete();
      } else {
        const error = await response.json();
        alert(`❌ Failed to complete job: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error completing job:', error);
      alert('❌ Failed to complete job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Complete Job</h2>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-orange-800">Job: {job.service}</h3>
              <div className="mt-2 text-sm text-orange-700">
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Description:</strong> {job.description}</p>
                <p><strong>Payment:</strong> R20 upon completion</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Before Image Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📸 Before Image (Required)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            {beforePreview ? (
              <div className="space-y-4">
                <img
                  src={beforePreview}
                  alt="Before"
                  className="mx-auto max-w-xs rounded-lg shadow-md"
                />
                <button
                  type="button"
                  onClick={() => beforeInputRef.current?.click()}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
                >
                  📷 Retake Before Photo
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-gray-400 text-4xl">📷</div>
                <div>
                  <button
                    type="button"
                    onClick={() => beforeInputRef.current?.click()}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
                  >
                    📸 Capture Before Photo
                  </button>
                </div>
                <p className="text-sm text-gray-500">
                  Take a photo showing the issue before you start working
                </p>
              </div>
            )}
            <input
              ref={beforeInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(e) => handleImageCapture(e.target.files[0], 'before')}
              className="hidden"
            />
          </div>
        </div>

        {/* After Image Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            📸 After Image (Required)
          </label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            {afterPreview ? (
              <div className="space-y-4">
                <img
                  src={afterPreview}
                  alt="After"
                  className="mx-auto max-w-xs rounded-lg shadow-md"
                />
                <button
                  type="button"
                  onClick={() => afterInputRef.current?.click()}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors"
                >
                  📷 Retake After Photo
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-gray-400 text-4xl">📷</div>
                <div>
                  <button
                    type="button"
                    onClick={() => afterInputRef.current?.click()}
                    className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
                  >
                    📸 Capture After Photo
                  </button>
                </div>
                <p className="text-sm text-gray-500">
                  Take a photo showing the completed work
                </p>
              </div>
            )}
            <input
              ref={afterInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(e) => handleImageCapture(e.target.files[0], 'after')}
              className="hidden"
            />
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || !beforeImage || !afterImage}
            className="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Completing Job...
              </div>
            ) : (
              '✅ Complete Job & Earn R20'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default JobCompletionForm;