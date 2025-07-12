import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState(''); // success, error
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setStatus('error');
      setMessage('Please enter your email address');
      return;
    }

    setIsLoading(true);
    setStatus('');
    setMessage('');

    try {
      const response = await fetch('http://localhost:5000/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (data.success) {
        setStatus('success');
        setMessage(data.message);
        setEmail(''); // Clear the email field
      } else {
        setStatus('error');
        setMessage(data.message || 'Failed to send password reset email');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setStatus('error');
      setMessage('Network error. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Reset Your Password</h1>
          <p>Enter your email address to receive password reset instructions</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              required
              className="form-input"
              disabled={isLoading}
            />
          </div>

          {status && (
            <div className={`message ${status === 'success' ? 'success-message' : 'error-message'}`}>
              <div className="message-icon">
                {status === 'success' ? '✓' : '✗'}
              </div>
              <p>{message}</p>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary full-width"
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
                Sending...
              </div>
            ) : (
              'Send Reset Instructions'
            )}
          </button>
        </form>

        <div className="auth-links">
          <p>
            Remember your password? <Link to="/login">Back to Login</Link>
          </p>
          <p>
            Don't have an account? <Link to="/register">Sign Up</Link>
          </p>
        </div>

        <div className="auth-footer">
          <div className="security-notice">
            <h4>🔒 Security Information</h4>
            <ul>
              <li>Reset links expire in 1 hour for security</li>
              <li>Only verified email addresses can reset passwords</li>
              <li>If you don't receive an email, check your spam folder</li>
              <li>Multiple requests may be rate-limited</li>
            </ul>
          </div>
          
          <div className="help-section">
            <h4>Need Help?</h4>
            <p>
              If you're having trouble accessing your account, 
              <a href="mailto:support@skillswap.com"> contact our support team</a>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
