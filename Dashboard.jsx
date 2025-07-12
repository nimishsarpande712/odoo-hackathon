import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from './Card';
import Notifications from './Notifications';
import SkillSwapRequests from './SkillSwapRequests';
import '../styles/Dashboard.css';

function Dashboard() {
  const [profiles, setProfiles] = useState([]);
  const [currentUserProfile, setCurrentUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showRequests, setShowRequests] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProfiles();
    fetchCurrentUserProfile();
    fetchUnreadNotificationCount();
    
    // Set up interval to check for new notifications every 30 seconds
    const interval = setInterval(fetchUnreadNotificationCount, 30000);
    return () => clearInterval(interval);
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

  const fetchProfiles = async () => {
    try {
      const response = await fetch('http://localhost:5000/profiles', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfiles(data.profiles || []);
      } else {
        setError('Failed to fetch profiles');
      }
    } catch (error) {
      console.error('Error fetching profiles:', error);
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

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading profiles...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Skill Swap Dashboard</h2>
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
          <button onClick={() => navigate('/all-profiles')} className="view-all-btn">
            View All Profiles
          </button>
          <button onClick={handleEditProfile} className="edit-profile-btn">
            Edit My Profile
          </button>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
          <button 
            className="btn btn-search"
            onClick={() => navigate('/search')}
          >
            🔍 Search Users
          </button>
        </div>
      </div>

      {currentUserProfile && (
        <div className="current-user-info">
          <h3>Welcome back, {currentUserProfile.name}!</h3>
          {currentUserProfile.offered_skills.length === 0 && currentUserProfile.wanted_skills.length === 0 && (
            <div className="profile-incomplete">
              <p>Your profile is incomplete. <button onClick={handleEditProfile} className="link-btn">Complete your profile</button> to appear in the dashboard.</p>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="profiles-section">
        <h3>Available Skill Swappers ({profiles.length})</h3>
        <p className="section-description">Connect with other users to swap skills. Your profile is not shown here to focus on potential matches.</p>
        
        {profiles.length === 0 ? (
          <div className="no-profiles">
            <p>No other completed profiles available yet. Be the first to complete your profile and encourage others to join!</p>
          </div>
        ) : (
          <div className="profiles-grid">
            {profiles.map(profile => (
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

export default Dashboard;
