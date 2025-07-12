import React, { useState } from 'react';
import '../styles/Card.css';
import SkillSwapRequestModal from './SkillSwapRequestModal';

function Card({ profile, showContactInfo = false, isCurrentUser = false }) {
  const [showRequestModal, setShowRequestModal] = useState(false);

  if (!profile) return null;

  const { name, location, offered_skills, wanted_skills, availability, email } = profile;

  const handleConnectClick = () => {
    setShowRequestModal(true);
  };

  const handleRequestSuccess = (data) => {
    // Show a more user-friendly success message
    const successMessage = `🎉 Skill swap request sent successfully to ${profile.name}! They will receive a notification and can respond to your request.`;
    alert(successMessage);
  };

  return (
    <div className={`Card ${isCurrentUser ? 'current-user-card' : ''}`}>
      <div className="card-header">
        <h3 className="user-name">{name}</h3>
        {location && <p className="user-location">📍 {location}</p>}
        {isCurrentUser && <span className="current-user-indicator">You</span>}
      </div>

      <div className="card-content">
        {offered_skills && offered_skills.length > 0 && (
          <div className="skills-section">
            <h4>🎯 Skills I Can Teach</h4>
            <div className="skills-list">
              {offered_skills.map((skill, index) => (
                <span key={index} className={`skill-tag offered ${skill.proficiency}`}>
                  {skill.name} ({skill.proficiency})
                </span>
              ))}
            </div>
          </div>
        )}

        {wanted_skills && wanted_skills.length > 0 && (
          <div className="skills-section">
            <h4>📚 Skills I Want to Learn</h4>
            <div className="skills-list">
              {wanted_skills.map((skill, index) => (
                <span key={index} className={`skill-tag wanted ${skill.desired_level}`}>
                  {skill.name} ({skill.desired_level})
                </span>
              ))}
            </div>
          </div>
        )}

        {availability && availability.length > 0 && (
          <div className="availability-section">
            <h4>⏰ Available</h4>
            <div className="availability-list">
              {availability.map((slot, index) => (
                <span key={index} className="availability-slot">
                  {slot.day} {slot.time_slot}
                </span>
              ))}
            </div>
          </div>
        )}

        {showContactInfo && email && (
          <div className="contact-section">
            <h4>📧 Contact</h4>
            <p className="email">{email}</p>
          </div>
        )}
      </div>

      <div className="card-footer">
        {!isCurrentUser && (
          <button className="contact-btn" onClick={handleConnectClick}>
            Connect for Skill Swap
          </button>
        )}
        {isCurrentUser && (
          <div className="current-user-footer">
            <p>This is your profile as others see it</p>
          </div>
        )}
      </div>

      {/* Skill Swap Request Modal */}
      {showRequestModal && (
        <SkillSwapRequestModal 
          recipientProfile={profile}
          onClose={() => setShowRequestModal(false)}
          onSuccess={handleRequestSuccess}
        />
      )}
    </div>
  );
}

export default Card;
