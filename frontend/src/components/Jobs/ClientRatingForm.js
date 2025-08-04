import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const ClientRatingForm = ({ job, onRatingSubmitted }) => {
  const [rating, setRating] = useState(0);
  const [review, setReview] = useState('');
  const [loading, setLoading] = useState(false);
  const [hoverRating, setHoverRating] = useState(0);
  const { user } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      alert('❌ Please select a rating (1-5 stars).');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('rating', rating.toString());
      formData.append('review', review);

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/jobs/${job.id}/rate-fixer`,
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
        alert(`✅ Rating submitted successfully! Money spent: R${result.money_spent}`);
        onRatingSubmitted && onRatingSubmitted(result);
      } else {
        const error = await response.json();
        alert(`❌ Failed to submit rating: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      alert('❌ Failed to submit rating. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const StarRating = ({ rating, hoverRating, setRating, setHoverRating }) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => setRating(star)}
            onMouseEnter={() => setHoverRating(star)}
            onMouseLeave={() => setHoverRating(0)}
            className={`text-3xl transition-colors ${
              star <= (hoverRating || rating)
                ? 'text-yellow-400'
                : 'text-gray-300'
            } hover:text-yellow-400`}
          >
            ⭐
          </button>
        ))}
      </div>
    );
  };

  const getRatingText = (rating) => {
    switch (rating) {
      case 1: return 'Very Poor';
      case 2: return 'Poor';
      case 3: return 'Average';
      case 4: return 'Good';
      case 5: return 'Excellent';
      default: return 'Select a rating';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Rate Your Fixer</h2>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">Job Completed: {job.service}</h3>
              <div className="mt-2 text-sm text-blue-700">
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Description:</strong> {job.description}</p>
                <p><strong>Completed:</strong> {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'Just now'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Rating Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            How would you rate the fixer's service? *
          </label>
          <div className="text-center space-y-3">
            <StarRating
              rating={rating}
              hoverRating={hoverRating}
              setRating={setRating}
              setHoverRating={setHoverRating}
            />
            <div className="text-lg font-medium text-gray-700">
              {getRatingText(hoverRating || rating)}
            </div>
          </div>
        </div>

        {/* Review Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Share your experience (Optional)
          </label>
          <textarea
            value={review}
            onChange={(e) => setReview(e.target.value)}
            placeholder="Tell other clients about your experience with this fixer..."
            rows="4"
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Before/After Images Preview */}
        {(job.before_image || job.after_image) && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Work Progress Photos
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {job.before_image && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Before:</p>
                  <img
                    src={`data:image/jpeg;base64,${job.before_image}`}
                    alt="Before work"
                    className="w-full h-48 object-cover rounded-lg shadow-md"
                  />
                </div>
              )}
              {job.after_image && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">After:</p>
                  <img
                    src={`data:image/jpeg;base64,${job.after_image}`}
                    alt="After work"
                    className="w-full h-48 object-cover rounded-lg shadow-md"
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Skip Rating
          </button>
          <button
            type="submit"
            disabled={loading || rating === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? (
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Submitting Rating...
              </div>
            ) : (
              '⭐ Submit Rating'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ClientRatingForm;