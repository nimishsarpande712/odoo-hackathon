import React, { useState } from 'react';
import '../styles/SkillSwapRequestModal.css';

function SkillSwapRequestModal({ recipientProfile, onClose, onSuccess }) {
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (message.trim().length < 10) {
      setError('Message must be at least 10 characters long');
      return;
    }
    
    if (message.length > 500) {
      setError('Message must not exceed 500 characters');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5000/skill-swap-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          requestee_id: recipientProfile.id,
          message: message.trim()
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        onSuccess && onSuccess(data);
        onClose();
      } else {
        setError(data.message || 'Failed to send request');
      }
    } catch (error) {
      console.error('Error sending skill swap request:', error);
      setError('Failed to connect to server');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSkillsSummary = (profile) => {
    const offeredSkills = profile.offered_skills?.map(skill => skill.name).join(', ') || 'None';
    const wantedSkills = profile.wanted_skills?.map(skill => skill.name).join(', ') || 'None';
    return { offeredSkills, wantedSkills };
  };

  const { offeredSkills, wantedSkills } = getSkillsSummary(recipientProfile);

  return (
    <div className="request-modal-overlay">
      <div className="request-modal">
        <div className="modal-header">
          <h3>Send Skill Swap Request</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div className="modal-content">
            <div className="recipient-info">
              <h4>To: {recipientProfile.name}</h4>
              {recipientProfile.location && (
                <p className="location">📍 {recipientProfile.location}</p>
              )}
              
              <div className="skills-summary">
                <div className="skills-section">
                  <h5>💡 Can teach:</h5>
                  <p>{offeredSkills}</p>
                </div>
                <div className="skills-section">
                  <h5>📚 Wants to learn:</h5>
                  <p>{wantedSkills}</p>
                </div>
              </div>
            </div>
            
            <div className="form-group">
              <label htmlFor="message">Your message: *</label>
              <div className="textarea-wrapper">
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Hi! I'm interested in a skill swap. I can teach you [your skills] and would love to learn [their skills]. When would be a good time to connect?"
                  rows={6}
                  maxLength={500}
                  required
                />
                <div className="char-count">
                  {message.length}/500 characters
                </div>
              </div>
            </div>
            
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}
          </div>
          
          <div className="modal-actions">
            <button 
              type="button" 
              className="cancel-btn"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="send-request-btn"
              disabled={isSubmitting || message.trim().length < 10}
              style={{ 
                display: 'flex', 
                visibility: 'visible',
                opacity: isSubmitting || message.trim().length < 10 ? '0.7' : '1'
              }}
            >
              <span className="btn-icon">📤</span>
              <span>{isSubmitting ? 'Sending...' : 'Send Request'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SkillSwapRequestModal;
