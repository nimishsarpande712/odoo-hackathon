import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Profile.css';

function Profile() {
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [offeredSkills, setOfferedSkills] = useState([]);
  const [wantedSkills, setWantedSkills] = useState([]);
  const [availability, setAvailability] = useState([]);
  const [newAvailability, setNewAvailability] = useState({ day: '', time_slot: '' });
  const [profileComplete, setProfileComplete] = useState(false);
  const navigate = useNavigate();

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const timeSlots = ['Morning', 'Afternoon', 'Evening', 'Night'];
  const proficiencyLevels = ['beginner', 'intermediate', 'advanced', 'expert'];

  useEffect(() => {
    fetchSkills();
    loadUserProfile();
  }, []);

  useEffect(() => {
    // Check if profile is complete
    const hasSkills = offeredSkills.length > 0 || wantedSkills.length > 0;
    setProfileComplete(hasSkills);
  }, [offeredSkills, wantedSkills]);

  const loadUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:5000/profile/current', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        const profile = data.profile;
        setOfferedSkills(profile.offered_skills || []);
        setWantedSkills(profile.wanted_skills || []);
        setAvailability(profile.availability || []);
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const fetchSkills = async () => {
    try {
      const response = await fetch('http://localhost:5000/skills', {
        credentials: 'include' // Include cookies/session
      });
      const data = await response.json();
      setSkills(data.skills || []);
    } catch (error) {
      console.error('Error fetching skills:', error);
    }
  };

  const addNewSkill = async () => {
    if (!newSkill.trim()) return;
    
    try {
      const response = await fetch('http://localhost:5000/add-skill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify({ name: newSkill, category: 'General' })
      });
      
      if (response.ok) {
        setNewSkill('');
        fetchSkills();
        alert('Skill added successfully!');
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error adding skill:', error);
      alert('Failed to add skill');
    }
  };

  const addOfferedSkill = async (skillId, proficiencyLevel) => {
    try {
      const response = await fetch('http://localhost:5000/user-skills-offered', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify({ skill_id: skillId, proficiency_level: proficiencyLevel })
      });
      
      if (response.ok) {
        alert('Offered skill added!');
        loadUserProfile(); // Refresh profile data
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error adding offered skill:', error);
      alert('Failed to add offered skill');
    }
  };

  const addWantedSkill = async (skillId, desiredLevel) => {
    try {
      const response = await fetch('http://localhost:5000/user-skills-wanted', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify({ skill_id: skillId, desired_level: desiredLevel })
      });
      
      if (response.ok) {
        alert('Wanted skill added!');
        loadUserProfile(); // Refresh profile data
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error adding wanted skill:', error);
      alert('Failed to add wanted skill');
    }
  };

  const addAvailability = async () => {
    if (!newAvailability.day || !newAvailability.time_slot) return;
    
    try {
      const response = await fetch('http://localhost:5000/availability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify(newAvailability)
      });
      
      if (response.ok) {
        setNewAvailability({ day: '', time_slot: '' });
        alert('Availability added!');
        loadUserProfile(); // Refresh profile data
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.message}`);
      }
    } catch (error) {
      console.error('Error adding availability:', error);
      alert('Failed to add availability');
    }
  };

  const handleCompleteProfile = () => {
    if (offeredSkills.length === 0 && wantedSkills.length === 0) {
      alert('Please add at least one skill you can offer or want to learn before completing your profile.');
      return;
    }
    navigate('/dashboard');
  };

  return (
    <div className="profile-container">
      <h2>Complete Your Profile</h2>
      
      {/* Profile Status */}
      <div className="section profile-status">
        <h3>Profile Status</h3>
        <p className={profileComplete ? 'status-complete' : 'status-incomplete'}>
          {profileComplete ? '✅ Profile Complete - Ready to appear in dashboard!' : '⚠️ Profile Incomplete - Add skills to appear in dashboard'}
        </p>
      </div>

      {/* Current Skills Display */}
      {(offeredSkills.length > 0 || wantedSkills.length > 0) && (
        <div className="section current-profile">
          <h3>Your Current Profile</h3>
          
          {offeredSkills.length > 0 && (
            <div className="current-skills">
              <h4>Skills You Offer:</h4>
              <div className="skills-display">
                {offeredSkills.map((skill, index) => (
                  <span key={index} className="skill-tag offered">
                    {skill.name} ({skill.proficiency})
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {wantedSkills.length > 0 && (
            <div className="current-skills">
              <h4>Skills You Want:</h4>
              <div className="skills-display">
                {wantedSkills.map((skill, index) => (
                  <span key={index} className="skill-tag wanted">
                    {skill.name} ({skill.desired_level})
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {availability.length > 0 && (
            <div className="current-availability">
              <h4>Your Availability:</h4>
              <div className="availability-display">
                {availability.map((slot, index) => (
                  <span key={index} className="availability-tag">
                    {slot.day} {slot.time_slot}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Add New Skill */}
      <div className="section">
        <h3>Add New Skill</h3>
        <div className="skill-input">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            placeholder="Enter new skill"
          />
          <button onClick={addNewSkill}>Add Skill</button>
        </div>
      </div>

      {/* Skills I Can Offer */}
      <div className="section">
        <h3>Skills I Can Offer</h3>
        {skills.map(skill => (
          <div key={skill.id} className="skill-item">
            <span>{skill.name}</span>
            <select onChange={(e) => addOfferedSkill(skill.id, e.target.value)}>
              <option value="">Select Proficiency</option>
              {proficiencyLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {/* Skills I Want to Learn */}
      <div className="section">
        <h3>Skills I Want to Learn</h3>
        {skills.map(skill => (
          <div key={skill.id} className="skill-item">
            <span>{skill.name}</span>
            <select onChange={(e) => addWantedSkill(skill.id, e.target.value)}>
              <option value="">Select Desired Level</option>
              {proficiencyLevels.map(level => (
                <option key={level} value={level}>{level}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      {/* Availability */}
      <div className="section">
        <h3>My Availability</h3>
        <div className="availability-input">
          <select 
            value={newAvailability.day}
            onChange={(e) => setNewAvailability({...newAvailability, day: e.target.value})}
          >
            <option value="">Select Day</option>
            {days.map(day => (
              <option key={day} value={day}>{day}</option>
            ))}
          </select>
          <select 
            value={newAvailability.time_slot}
            onChange={(e) => setNewAvailability({...newAvailability, time_slot: e.target.value})}
          >
            <option value="">Select Time</option>
            {timeSlots.map(slot => (
              <option key={slot} value={slot}>{slot}</option>
            ))}
          </select>
          <button onClick={addAvailability}>Add Availability</button>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={handleCompleteProfile} className="complete-btn">
          {profileComplete ? 'Go to Dashboard' : 'Complete Profile Later'}
        </button>
        <button onClick={() => navigate('/dashboard')} className="view-dashboard-btn">
          View Dashboard
        </button>
      </div>
    </div>
  );
}

export default Profile;
