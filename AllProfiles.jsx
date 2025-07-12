import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from './Card';
import Notifications from './Notifications';
import SkillSwapRequests from './SkillSwapRequests';
import '../styles/Dashboard.css';

function AllProfiles() {
  const [profiles, setProfiles] = useState([]);
  const [currentUserProfile, setCurrentUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showRequests, setShowRequests] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllProfiles();
    fetchCurrentUserProfile();
    fetchUnreadNotificationCount();
  }, []);

  const fetchUnreadNotificationCount = async () => {
    try {
      const response = await fetch('http://localhost:5000/notifications?unread_only=true', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadNotificationCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Error fetching unread notification count:', error);
    }
  };

  const fetchAllProfiles = async () => {
    try {
      const response = await fetch('http://localhost:5000/all-profiles', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfiles(data.profiles || []);
      } else {
        setError('Failed to fetch profiles');
      }
    } catch (error) {
      console.error('Error fetching all profiles:', error);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentUserProfile = async () => {
    try {
      const response = await fetch('http://localhost:5000/profile/current', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentUserProfile(data.profile);
      }
    } catch (error) {
      console.error('Error fetching current user profile:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:5000/logout', {
        method: 'POST',
        credentials: 'include'
      });
      navigate('/login');
    } catch (error) {
      console.error('Error logging out:', error);
      navigate('/login');
    }
  };

  const handleEditProfile = () => {
    navigate('/profile');
  };

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading all profiles...</div>
      </div>
    );
  }

  // Separate current user and other profiles
  const currentUserCard = profiles.find(profile => profile.is_current_user);
  const otherProfiles = profiles.filter(profile => !profile.is_current_user);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>All Registered Profiles</h2>
        <div className="header-buttons">
          <button 
            onClick={() => setShowNotifications(true)} 
            className="notification-btn"
            title="View Notifications"
          >
            🔔 Notifications
            {unreadNotificationCount > 0 && (
              <span className="notification-badge">{unreadNotificationCount}</span>
            )}
          </button>
          <button 
            onClick={() => setShowRequests(true)} 
            className="requests-btn"
            title="Manage Skill Swap Requests"
          >
            🤝 Requests
          </button>
          <button onClick={handleBackToDashboard} className="edit-profile-btn">
            Back to Dashboard
          </button>
          <button onClick={handleEditProfile} className="edit-profile-btn">
            Edit My Profile
          </button>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>

      {currentUserProfile && (
        <div className="current-user-info">
          <h3>Viewing all {profiles.length} registered profiles</h3>
          <p>This view shows all public profiles in the system, including your own.</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {/* Current User's Profile Section */}
      {currentUserCard && (
        <div className="profiles-section">
          <h3>Your Profile</h3>
          <div className="profiles-grid">
            <div className="current-user-profile-wrapper">
              <Card 
                profile={currentUserCard}
                showContactInfo={false}
                isCurrentUser={true}
              />
            </div>
          </div>
        </div>
      )}

      {/* Other Users' Profiles Section */}
      <div className="profiles-section">
        <h3>Other Users ({otherProfiles.length})</h3>
        
        {otherProfiles.length === 0 ? (
          <div className="no-profiles">
            <p>No other completed profiles available yet.</p>
          </div>
        ) : (
          <div className="profiles-grid">
            {otherProfiles.map(profile => (
              <Card 
                key={profile.id} 
                profile={profile}
                showContactInfo={true}
              />
            ))}
          </div>
        )}
      </div>

      {/* Notifications Modal */}
      {showNotifications && (
        <Notifications onClose={() => setShowNotifications(false)} />
      )}

      {/* Skill Swap Requests Modal */}
      {showRequests && (
        <SkillSwapRequests onClose={() => setShowRequests(false)} />
      )}
    </div>
  );
}

export default AllProfiles;
