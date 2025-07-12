import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import '../styles/Profile.css';

const UserRating = ({ userId, currentUserId }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState('');
  const [userRatings, setUserRatings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      await fetchRatings();
    };
    fetchData();
  }, [userId, fetchRatings]);

  const fetchRatings = React.useCallback(async () => {
    try {
      const [avgResponse, detailsResponse] = await Promise.all([
        axios.get(`/ratings/${userId}`),
        axios.get(`/ratings/${userId}/details`)
      ]);

      setUserRatings({
        average: avgResponse.data.average_rating,
        total: avgResponse.data.total_ratings,
        details: detailsResponse.data
      });
    } catch (error) {
      console.error('Error fetching ratings:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rating) return;

    setSubmitting(true);
    try {
      await axios.post('/ratings', {
        user_id: currentUserId,
        rated_user_id: userId,
        rating,
        comment
      });
      
      setRating(0);
      setComment('');
      await fetchRatings();
    } catch (error) {
      console.error('Error submitting rating:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return (
    <div className="rating-section">
      <div className="average-rating">
        <div className="rating-number">{userRatings.average}</div>
        <div className="rating-stats">
          <div className="review-stars">
            {'★'.repeat(Math.round(userRatings.average))}
            {'☆'.repeat(5 - Math.round(userRatings.average))}
          </div>
          <div className="total-ratings">
            {userRatings.total} {userRatings.total === 1 ? 'review' : 'reviews'}
          </div>
        </div>
      </div>

      {userId !== currentUserId && (
        <form onSubmit={handleSubmit} className={submitting ? 'loading' : ''}>
          <div className="rating-stars">
            {[1, 2, 3, 4, 5].map((star) => (
              <span
                key={star}
                className={`star ${star <= (hoveredRating || rating) ? 'active' : ''}`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
              >
                ★
              </span>
            ))}
          </div>
          
          <textarea
            className="rating-input"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Write your review (optional)"
            rows="3"
            disabled={submitting}
          />
          
          <button
            className="rating-submit"
            type="submit"
            disabled={!rating || submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Review'}
          </button>
        </form>
      )}

      <div className="reviews-section">
        {userRatings.details.ratings.map((review, index) => (
          <div key={index} className="review-card">
            <div className="review-header">
              <div className="review-stars">
                {'★'.repeat(review.rating)}
                {'☆'.repeat(5 - review.rating)}
              </div>
              <div className="review-date">
                {new Date(review.created_at).toLocaleDateString()}
              </div>
            </div>
            <div className="reviewer-name">{review.reviewer_name}</div>
            {review.comment && (
              <div className="review-comment">{review.comment}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserRating;
