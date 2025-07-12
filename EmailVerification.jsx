import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import '../styles/Auth.css';

const EmailVerification = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('Verifying your email...');
  const [resendEmail, setResendEmail] = useState('');
  const [resendLoading, setResendLoading] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link. Please check your email and try again.');
      return;
    }

    const verifyEmail = async (token) => {
      try {
        const response = await fetch('http://localhost:5000/verify-email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (data.success) {
          setStatus('success');
          setMessage(data.message);
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/login', { 
              state: { message: 'Email verified successfully! You can now log in.' }
            });
          }, 3000);
        } else {
          setStatus('error');
          setMessage(data.message || 'Email verification failed. Please try again.');
        }
      } catch (error) {
        console.error('Verification error:', error);
        setStatus('error');
        setMessage('Network error. Please check your connection and try again.');
      }
    };

    verifyEmail(token);
  }, [searchParams, navigate]);

  const handleResendVerification = async (e) => {
    e.preventDefault();
    
    if (!resendEmail) {
      alert('Please enter your email address');
      return;
    }

    setResendLoading(true);

    try {
      const response = await fetch('http://localhost:5000/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email: resendEmail }),
      });

      const data = await response.json();

      if (data.success) {
        alert('Verification email sent! Please check your inbox.');
        setResendEmail('');
      } else {
        alert(data.message || 'Failed to send verification email');
      }
    } catch (error) {
      console.error('Resend error:', error);
      alert('Network error. Please try again.');
    } finally {
      setResendLoading(false);
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'verifying':
        return <div className="spinner"></div>;
      case 'success':
        return <div className="success-icon">✓</div>;
      case 'error':
        return <div className="error-icon">✗</div>;
      default:
        return null;
    }
  };

  const getStatusClass = () => {
    switch (status) {
      case 'success':
        return 'verification-success';
      case 'error':
        return 'verification-error';
      default:
        return 'verification-pending';
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Email Verification</h1>
          <p>SkillSwap Account Verification</p>
        </div>

        <div className={`verification-status ${getStatusClass()}`}>
          {getStatusIcon()}
          <div className="status-message">
            <h3>{status === 'verifying' ? 'Verifying...' : status === 'success' ? 'Verified!' : 'Verification Failed'}</h3>
            <p>{message}</p>
          </div>
        </div>

        {status === 'success' && (
          <div className="success-actions">
            <p className="redirect-notice">
              You will be redirected to login in a few seconds...
            </p>
            <button
              onClick={() => navigate('/login')}
              className="btn btn-primary"
            >
              Go to Login Now
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="error-actions">
            <div className="resend-section">
              <h4>Need a new verification email?</h4>
              <form onSubmit={handleResendVerification} className="resend-form">
                <div className="form-group">
                  <input
                    type="email"
                    placeholder="Enter your email address"
                    value={resendEmail}
                    onChange={(e) => setResendEmail(e.target.value)}
                    required
                    className="form-input"
                  />
                </div>
                <button
                  type="submit"
                  disabled={resendLoading}
                  className="btn btn-secondary"
                >
                  {resendLoading ? 'Sending...' : 'Resend Verification Email'}
                </button>
              </form>
            </div>

            <div className="alternative-actions">
              <button
                onClick={() => navigate('/login')}
                className="btn btn-outline"
              >
                Back to Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="btn btn-outline"
              >
                Create New Account
              </button>
            </div>
          </div>
        )}

        <div className="auth-footer">
          <div className="security-notice">
            <p>🔒 <strong>Security Notice:</strong> Verification links expire after 24 hours for your security.</p>
          </div>
          <div className="help-links">
            <p>Having trouble? <a href="mailto:support@skillswap.com">Contact Support</a></p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification;
