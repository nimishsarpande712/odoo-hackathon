import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import '../styles/SearchUsers.css';

const SearchUsers = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/users/search');
      const users = response.data.users || [];
      setUsers(users);
      setFilteredUsers(users);
    } catch (error) {
      console.error('Error fetching users:', error);
      // Fallback to admin endpoint
      try {
        const response = await axios.get('http://localhost:5000/admin/users');
        const users = response.data.users || [];
        // Add empty skills array for fallback data
        const usersWithSkills = users.map(user => ({
          ...user,
          skills: []
        }));
        setUsers(usersWithSkills);
        setFilteredUsers(usersWithSkills);
      } catch (fallbackError) {
        console.error('Fallback fetch failed:', fallbackError);
        setUsers([]);
        setFilteredUsers([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const searchUsers = useCallback(async (term) => {
    if (!term.trim()) {
      return users;
    }
    
    try {
      const response = await axios.get(`http://localhost:5000/api/users/search?q=${encodeURIComponent(term)}`);
      return response.data.users || [];
    } catch (error) {
      console.error('Error searching users:', error);
      // Fallback to client-side filtering
      return users.filter(user => 
        user.skills?.some(skill => 
          skill.toLowerCase().includes(term.toLowerCase())
        ) ||
        user.name.toLowerCase().includes(term.toLowerCase()) ||
        user.email.toLowerCase().includes(term.toLowerCase())
      );
    }
  }, [users]);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    const delayedSearch = setTimeout(async () => {
      setLoading(true);
      if (searchTerm.trim() === '') {
        setFilteredUsers(users);
      } else {
        const results = await searchUsers(searchTerm);
        setFilteredUsers(results);
      }
      setLoading(false);
    }, 300); // Debounce search
    
    return () => clearTimeout(delayedSearch);
  }, [searchTerm, users, searchUsers]);

  return (
    <div className="search-container">
      <div className="search-header">
        <h2>Find Users by Skills</h2>
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by skill (e.g., Photoshop, Excel) or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="search-icon">🔍</div>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading users...</div>
      ) : (
        <div className="users-grid">
          {filteredUsers.map(user => (
            <div key={user.id} className="user-card">
              <div className="user-avatar">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="user-info">
                <h3>{user.name}</h3>
                <p className="user-email">{user.email}</p>
                <div className="user-skills">
                  {user.skills.map((skill, index) => (
                    <span key={index} className="skill-tag">
                      {skill}
                    </span>
                  ))}
                </div>
                <button className="connect-btn">Connect</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {filteredUsers.length === 0 && !loading && (
        <div className="no-results">
          No users found matching "{searchTerm}"
        </div>
      )}
    </div>
  );
};

export default SearchUsers;
