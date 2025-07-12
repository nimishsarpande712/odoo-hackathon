import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FormValidator } from '../utils/validation';
import '../styles/Auth.css';

function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [validationErrors, setValidationErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const validateField = (name, value) => {
    let validation;
    
    switch (name) {
      case 'username':
        // Username can be either name or email
        const isEmail = value.includes('@');
        if (isEmail) {
          validation = FormValidator.validateEmail(value);
        } else {
          validation = FormValidator.validateName(value);
        }
        break;
      case 'password':
        if (!value) {
          validation = { isValid: false, errors: ['Password is required'] };
        } else {
          validation = { isValid: true, errors: [] };
        }
        break;
      default:
        validation = { isValid: true, errors: [] };
    }
    
    setValidationErrors(prev => ({
      ...prev,
      [name]: validation.errors
    }));
    
    return validation.isValid;
  };

  const validateForm = () => {
    const errors = {};
    let isFormValid = true;
    
    // Validate username (can be name or email)
    const isEmail = formData.username.includes('@');
    let usernameValidation;
    
    if (isEmail) {
      usernameValidation = FormValidator.validateEmail(formData.username);
    } else {
      usernameValidation = FormValidator.validateName(formData.username);
    }
    
    if (!usernameValidation.isValid) {
      errors.username = usernameValidation.errors;
      isFormValid = false;
    }
    
    // Validate password
    if (!formData.password) {
      errors.password = ['Password is required'];
      isFormValid = false;
    }
    
    setValidationErrors(errors);
    return isFormValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // SKIP EMAIL VERIFICATION CHECK - Allow login without verification
        // if (!data.email_verified) {
        //   alert('Please verify your email address before logging in. Check your inbox for the verification link.');
        //   return;
        // }
        
        // Check if user has completed their profile
        try {
          const profileResponse = await fetch('http://localhost:5000/profile/current', {
            credentials: 'include'
          });
          
          if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            const profile = profileData.profile;
            
            // Check if user has at least one offered or wanted skill
            const hasCompletedProfile = (profile.offered_skills && profile.offered_skills.length > 0) || 
                                      (profile.wanted_skills && profile.wanted_skills.length > 0);
            
            if (hasCompletedProfile) {
              navigate('/dashboard');
            } else {
              navigate('/profile');
            }
          } else {
            // If can't fetch profile, go to profile page to complete it
            navigate('/profile');
          }
        } catch (profileError) {
          console.error('Error checking profile completion:', profileError);
          navigate('/profile');
        }
      } else {
        // Handle specific error types
        if (data.error_code === 'AUTH_003') {
          // Email not verified - MAKE THIS OPTIONAL
          // const shouldResend = window.confirm(
          //   'Your email address is not verified. Would you like us to send a new verification email?'
          // );
          // if (shouldResend) {
          //   handleResendVerification();
          // }
          alert(data.message || 'Login failed');
        } else if (data.error_code === 'AUTH_002') {
          // Account locked
          alert(data.message + '\n\nYou can reset your password to unlock your account.');
        } else {
          alert(data.message || 'Login failed');
        }
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Error connecting to server. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendVerification = async () => {
    const email = formData.username.includes('@') ? formData.username : '';
    
    if (!email) {
      const userEmail = prompt('Please enter your email address to resend verification:');
      if (!userEmail) return;
      
      try {
        const response = await fetch('http://localhost:5000/resend-verification', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ email: userEmail })
        });
        
        const data = await response.json();
        alert(data.message);
      } catch (error) {
        alert('Failed to send verification email. Please try again.');
      }
    } else {
      try {
        const response = await fetch('http://localhost:5000/resend-verification', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        alert(data.message);
      } catch (error) {
        alert('Failed to send verification email. Please try again.');
      }
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    setFormData({
      ...formData,
      [name]: value
    });
    
    // Real-time validation
    setTimeout(() => validateField(name, value), 300);
  };

  const renderFieldErrors = (fieldName) => {
    const errors = validationErrors[fieldName];
    if (!errors || errors.length === 0) return null;
    
    return (
      <div className="field-errors">
        {errors.map((error, index) => (
          <small key={index} className="error-text">{error}</small>
        ))}
      </div>
    );
  };

  const getFieldClassName = (fieldName) => {
    const errors = validationErrors[fieldName];
    if (!errors) return '';
    return errors.length > 0 ? 'field-error' : 'field-valid';
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Sign in to your SkillSwap account</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username or Email *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className={`form-input ${getFieldClassName('username')}`}
              required
              placeholder="Enter your name or email"
              disabled={isSubmitting}
            />
            {renderFieldErrors('username')}
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${getFieldClassName('password')}`}
              required
              placeholder="Enter your password"
              disabled={isSubmitting}
            />
            {renderFieldErrors('password')}
          </div>
          
          <div className="form-actions">
            <button 
              type="submit" 
              disabled={isSubmitting}
              className="btn btn-primary full-width"
            >
              {isSubmitting ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  Signing in...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </div>
        </form>
        
        <div className="auth-links">
          <div className="forgot-password-link">
            <a href="/forgot-password">Forgot your password?</a>
          </div>
          <div className="signup-link">
            <p>Don't have an account? <a href="/register">Sign up here</a></p>
          </div>
          <div className="verification-link">
            <p>
              Need to verify your email? 
              <button 
                type="button" 
                className="link-button" 
                onClick={handleResendVerification}
              >
                Resend verification email
              </button>
            </p>
          </div>
        </div>

        <div className="auth-footer">
          <div className="security-notice">
            <p>🔒 Your account is protected with secure authentication</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
