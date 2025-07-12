import React, { useState, useEffect } from 'react';
import '../styles/AdminLogin.css';

function AdminLogin() {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('skills');
  const [skills, setSkills] = useState([]);
  const [users, setUsers] = useState([]);
  const [swaps, setSwaps] = useState([]);
  const [message, setMessage] = useState('');
  const [messageTitle, setMessageTitle] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch real data from backend
  useEffect(() => {
    if (isLoggedIn) {
      fetchAllData();
    }
  }, [isLoggedIn]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchSkills(),
        fetchUsers(),
        fetchSwaps()
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSkills = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/skills', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setSkills(data.skills || []);
      }
    } catch (error) {
      console.error('Error fetching skills:', error);
      // Fallback to sample data if backend not available
      setSkills([
        { id: 1, user: 'John', skill: 'Python Programming', status: 'pending' },
        { id: 2, user: 'Alice', skill: 'Web Design', status: 'pending' }
      ]);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/users', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fallback to sample data if backend not available
      setUsers([
        { id: 1, name: 'John Doe', email: 'john@email.com', status: 'active' },
        { id: 2, name: 'Alice Smith', email: 'alice@email.com', status: 'active' }
      ]);
    }
  };

  const fetchSwaps = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/swaps', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setSwaps(data.swaps || []);
      }
    } catch (error) {
      console.error('Error fetching swaps:', error);
      // Fallback to sample data if backend not available
      setSwaps([
        { id: 1, from: 'John', to: 'Alice', skill: 'Python for Design', status: 'pending' },
        { id: 2, from: 'Bob', to: 'Charlie', skill: 'Marketing for Code', status: 'accepted' }
      ]);
    }
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/admin/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        setIsLoggedIn(true);
        alert('Admin login successful!');
      } else {
        alert('Invalid credentials!');
      }
    } catch (error) {
      // Fallback to local check if backend not available
      if (credentials.username === 'admin' && credentials.password === 'admin123') {
        setIsLoggedIn(true);
        alert('Admin login successful!');
      } else {
        alert('Invalid credentials!');
      }
    } finally {
      setLoading(false);
    }
  };

  const rejectSkill = async (skillId) => {
    try {
      const response = await fetch('http://localhost:5000/admin/reject_skill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ skill_id: skillId })
      });

      if (response.ok) {
        setSkills(skills.map(skill => 
          skill.id === skillId ? { ...skill, status: 'rejected' } : skill
        ));
        alert('Skill rejected successfully!');
      }
    } catch (error) {
      // Fallback to local update
      setSkills(skills.map(skill => 
        skill.id === skillId ? { ...skill, status: 'rejected' } : skill
      ));
      alert('Skill rejected successfully!');
    }
  };

  const banUser = async (userId) => {
    try {
      const response = await fetch('http://localhost:5000/admin/ban_user', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ user_id: userId })
      });

      if (response.ok) {
        setUsers(users.map(user => 
          user.id === userId ? { ...user, status: 'banned' } : user
        ));
        alert('User banned successfully!');
      }
    } catch (error) {
      // Fallback to local update
      setUsers(users.map(user => 
        user.id === userId ? { ...user, status: 'banned' } : user
      ));
      alert('User banned successfully!');
    }
  };

  const sendMessage = async () => {
    if (message.trim()) {
      try {
        const response = await fetch('http://localhost:5000/admin/send_message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ 
            title: messageTitle.trim() || 'Admin Broadcast',
            message: message.trim() 
          })
        });

        if (response.ok) {
          const data = await response.json();
          alert(`${data.message}\nUsers notified: ${data.users_notified || 'N/A'}`);
          setMessage('');
          setMessageTitle('');
        }
      } catch (error) {
        // Fallback
        alert(`Platform message sent: "${message}"`);
        setMessage('');
        setMessageTitle('');
      }
    }
  };

  const downloadReports = async () => {
    try {
      const response = await fetch('http://localhost:5000/admin/download_reports', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'admin-report.json';
        link.click();
        alert('Report downloaded successfully!');
      }
    } catch (error) {
      // Fallback to local data
      const reportData = {
        totalUsers: users.length,
        totalSkills: skills.length,
        totalSwaps: swaps.length,
        timestamp: new Date().toLocaleString()
      };
      
      const dataStr = JSON.stringify(reportData, null, 2);
      const dataBlob = new Blob([dataStr], {type: 'application/json'});
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'admin-report.json';
      link.click();
      alert('Report downloaded successfully!');
    }
  };

  if (isLoggedIn) {
    return (
      <div className="admin-dashboard">
        <h2>🔧 Admin Dashboard</h2>
        
        <div className="admin-tabs">
          <button onClick={() => setActiveTab('skills')} className={activeTab === 'skills' ? 'active' : ''}>
            Reject Skills
          </button>
          <button onClick={() => setActiveTab('users')} className={activeTab === 'users' ? 'active' : ''}>
            Ban Users
          </button>
          <button onClick={() => setActiveTab('swaps')} className={activeTab === 'swaps' ? 'active' : ''}>
            Monitor Swaps
          </button>
          <button onClick={() => setActiveTab('messages')} className={activeTab === 'messages' ? 'active' : ''}>
            Send Messages
          </button>
          <button onClick={() => setActiveTab('reports')} className={activeTab === 'reports' ? 'active' : ''}>
            Download Reports
          </button>
        </div>

        <div className="admin-content">
          {activeTab === 'skills' && (
            <div className="skills-section">
              <h3>Skills Management</h3>
              {skills.map(skill => (
                <div key={skill.id} className="admin-item">
                  <span>{skill.user} - {skill.skill} ({skill.status})</span>
                  {skill.status === 'pending' && (
                    <button onClick={() => rejectSkill(skill.id)} className="reject-btn">
                      Reject
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {activeTab === 'users' && (
            <div className="users-section">
              <h3>User Management</h3>
              {users.map(user => (
                <div key={user.id} className="admin-item">
                  <span>{user.name} - {user.email} ({user.status})</span>
                  {user.status === 'active' && (
                    <button onClick={() => banUser(user.id)} className="ban-btn">
                      Ban User
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {activeTab === 'swaps' && (
            <div className="swaps-section">
              <h3>Swaps Monitoring</h3>
              {swaps.map(swap => (
                <div key={swap.id} className="admin-item">
                  <span>{swap.from} ↔ {swap.to} ({swap.skill}) - {swap.status}</span>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'messages' && (
            <div className="messages-section">
              <h3>Send Platform Messages</h3>
              <input
                type="text"
                value={messageTitle}
                onChange={(e) => setMessageTitle(e.target.value)}
                placeholder="Message title (optional)"
                className="message-title-input"
              />
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your platform-wide message..."
                className="message-input"
              />
              <button onClick={sendMessage} className="send-msg-btn">
                Send Broadcast Message
              </button>
              <p className="broadcast-info">
                💡 This will send a notification to all active users
              </p>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="reports-section">
              <h3>Download Reports</h3>
              <div className="report-stats">
                <p>Total Users: {users.length}</p>
                <p>Total Skills: {skills.length}</p>
                <p>Total Swaps: {swaps.length}</p>
              </div>
              <button onClick={downloadReports} className="download-btn">
                Download Report
              </button>
            </div>
          )}
        </div>

        <button onClick={() => setIsLoggedIn(false)} className="logout-btn">
          Logout
        </button>
      </div>
    );
  }

  return (
    <div className="admin-login-container">
      <div className="admin-login-box">
        <h2>🔐 Admin Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              name="username"
              placeholder="Username"
              value={credentials.username}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={credentials.password}
              onChange={handleChange}
              required
            />
          </div>
          <button type="submit" className="login-btn">
            Login
          </button>
        </form>
        <p className="admin-hint">
          Hint: username: admin, password: admin123
        </p>
      </div>
    </div>
  );
}

export default AdminLogin;
