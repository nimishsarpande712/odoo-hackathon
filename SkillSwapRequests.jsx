import React, { useState, useEffect } from 'react';
import '../styles/SkillSwapRequests.css';
import Chat from './Chat';

function SkillSwapRequests({ onClose }) {
  const [requests, setRequests] = useState({ sent: [], received: [] });
  const [activeTab, setActiveTab] = useState('received');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showChat, setShowChat] = useState(false);
  const [chatRequest, setChatRequest] = useState(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await fetch('http://localhost:5000/skill-swap-requests', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setRequests(data.requests);
      } else {
        setError('Failed to fetch requests');
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const respondToRequest = async (requestId, response) => {
    try {
      const res = await fetch(`http://localhost:5000/skill-swap-request/${requestId}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ response })
      });
      
      if (res.ok) {
        // Update the request status locally
        setRequests(prev => ({
          ...prev,
          received: prev.received.map(req => 
            req.id === requestId 
              ? { ...req, status: response }
              : req
          )
        }));
        alert(`Request ${response} successfully!`);
        
        // If accepted, show chat option
        if (response === 'accepted') {
          setShowChat(true);
          setChatRequest(requestId);
        }
      } else {
        const data = await res.json();
        alert(data.message || `Failed to ${response} request`);
      }
    } catch (error) {
      console.error(`Error ${response} request:`, error);
      alert(`Failed to ${response} request`);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', className: 'status-pending' },
      accepted: { label: 'Accepted', className: 'status-accepted' },
      declined: { label: 'Declined', className: 'status-declined' },
      cancelled: { label: 'Cancelled', className: 'status-cancelled' }
    };
    
    const config = statusConfig[status] || statusConfig.pending;
    return <span className={`status-badge ${config.className}`}>{config.label}</span>;
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="requests-popup">
        <div className="requests-header">
          <h3>Skill Swap Requests</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="requests-content">
          <div className="loading">Loading requests...</div>
        </div>
      </div>
    );
  }

  const currentRequests = requests[activeTab] || [];

  return (
    <div className="requests-popup">
      <div className="requests-header">
        <h3>Skill Swap Requests</h3>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      
      <div className="requests-tabs">
        <button 
          className={`tab-btn ${activeTab === 'received' ? 'active' : ''}`}
          onClick={() => setActiveTab('received')}
        >
          Received ({requests.received?.length || 0})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'sent' ? 'active' : ''}`}
          onClick={() => setActiveTab('sent')}
        >
          Sent ({requests.sent?.length || 0})
        </button>
      </div>
      
      <div className="requests-content">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {currentRequests.length === 0 ? (
          <div className="no-requests">
            <p>No {activeTab} requests yet</p>
          </div>
        ) : (
          <div className="requests-list">
            {currentRequests.map(request => (
              <div key={request.id} className="request-item">
                <div className="request-header">
                  <div className="user-info">
                    <h4>{request.user_name}</h4>
                    <span className="user-email">{request.user_email}</span>
                  </div>
                  {getStatusBadge(request.status)}
                </div>
                
                {request.message && (
                  <div className="request-message">
                    <p>"{request.message}"</p>
                  </div>
                )}
                
                <div className="request-footer">
                  <span className="request-date">
                    {formatDate(request.created_at)}
                  </span>
                  
                  {activeTab === 'received' && request.status === 'pending' && (
                    <div className="request-actions">
                      <button 
                        className="accept-btn"
                        onClick={() => respondToRequest(request.id, 'accepted')}
                      >
                        Accept
                      </button>
                      <button 
                        className="decline-btn"
                        onClick={() => respondToRequest(request.id, 'declined')}
                      >
                        Decline
                      </button>
                    </div>
                  )}
                  
                  {request.status === 'accepted' && (
                    <div className="request-actions">
                      <button 
                        className="chat-btn"
                        onClick={() => {
                          setShowChat(true);
                          setChatRequest(request);
                        }}
                      >
                        💬 Start Chat
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Chat Modal */}
      {showChat && chatRequest && (
        <Chat
          requestId={chatRequest.id}
          recipientName={chatRequest.user_name}
          onClose={() => {
            setShowChat(false);
            setChatRequest(null);
          }}
        />
      )}
    </div>
  );
}

export default SkillSwapRequests;
