import React, { useState } from 'react';
import '../styles/Rating.css';

const StarRating = ({ rating, onRating, readOnly = false, size = 'medium' }) => {
  const [hover, setHover] = useState(0);

  const handleClick = (value) => {
    if (!readOnly && onRating) {
      onRating(value);
    }
  };

  return (
    <div className={`star-rating ${size} ${readOnly ? 'readonly' : ''}`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`star ${
            star <= (hover || rating) ? 'filled' : 'empty'
          }`}
          onClick={() => handleClick(star)}
          onMouseEnter={() => !readOnly && setHover(star)}
          onMouseLeave={() => !readOnly && setHover(0)}
        >
          ★
        </span>
      ))}
    </div>
  );
};

const RatingModal = ({ isOpen, onClose, userName, onSubmit }) => {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    setLoading(true);
    try {
      await onSubmit({ rating, comment });
      setRating(0);
      setComment('');
      onClose();
    } catch (error) {
      alert('Failed to submit rating. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="rating-modal-overlay">
      <div className="rating-modal">
        <div className="rating-modal-header">
          <h3>Rate {userName}</h3>
          <button onClick={onClose} className="close-btn">×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="rating-form">
          <div className="rating-section">
            <label>Your Rating:</label>
            <StarRating rating={rating} onRating={setRating} size="large" />
          </div>
          
          <div className="comment-section">
            <label>Comment (optional):</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Share your experience..."
              maxLength={500}
            />
          </div>
          
          <div className="rating-actions">
            <button type="button" onClick={onClose} className="cancel-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading || rating === 0} className="submit-btn">
              {loading ? 'Submitting...' : 'Submit Rating'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export { StarRating, RatingModal };
