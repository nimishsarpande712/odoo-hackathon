import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FormValidator } from '../utils/validation';
import '../styles/Auth.css';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    location: '',
    is_public: true
  });
  
  const [validationErrors, setValidationErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [emailChecked, setEmailChecked] = useState(false);
  const [emailAvailable, setEmailAvailable] = useState(null);
  const navigate = useNavigate();

  const validateField = (name, value) => {
    let validation;
    
    switch (name) {
      case 'username':
        validation = FormValidator.validateName(value);
        break;
      case 'email':
        validation = FormValidator.validateEmail(value);
        break;
      case 'password':
        validation = FormValidator.validatePassword(value);
        setPasswordStrength(FormValidator.getPasswordStrength(value));
        break;
      case 'location':
        validation = FormValidator.validateLocation(value);
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
    
    // Validate all fields
    const nameValidation = FormValidator.validateName(formData.username);
    const emailValidation = FormValidator.validateEmail(formData.email);
    const passwordValidation = FormValidator.validatePassword(formData.password);
    const locationValidation = FormValidator.validateLocation(formData.location);
    
    if (!nameValidation.isValid) {
      errors.username = nameValidation.errors;
      isFormValid = false;
    }
    
    if (!emailValidation.isValid) {
      errors.email = emailValidation.errors;
      isFormValid = false;
    }
    
    if (!passwordValidation.isValid) {
      errors.password = passwordValidation.errors;
      isFormValid = false;
    }
    
    if (!locationValidation.isValid) {
      errors.location = locationValidation.errors;
      isFormValid = false;
    }
    
    setValidationErrors(errors);
    return isFormValid;
  };

  // Password strength checker
  const checkPasswordStrength = (password) => {
    const criteria = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    const score = Object.values(criteria).filter(Boolean).length;
    
    if (score <= 2) return { strength: 'weak', color: '#ff4444', text: 'Weak' };
    if (score <= 3) return { strength: 'medium', color: '#ffaa00', text: 'Medium' };
    if (score <= 4) return { strength: 'good', color: '#44aa44', text: 'Good' };
    return { strength: 'strong', color: '#00aa44', text: 'Strong' };
  };

  // Email availability checker (debounced)
  const checkEmailAvailability = async (email) => {
    if (!email || !email.includes('@')) return;
    
    try {
      setEmailChecked(true);
      const response = await fetch(`http://localhost:5000/check-email?email=${encodeURIComponent(email)}`);
      const data = await response.json();
      setEmailAvailable(data.available);
    } catch (error) {
      console.error('Email check failed:', error);
      setEmailAvailable(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies/session
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Show success message with email verification notice
        alert(`Registration successful! 
        
📧 We've sent a verification email to ${formData.email}
        
Please check your inbox and click the verification link to activate your account. 
        
You can also check your spam/junk folder if you don't see it within a few minutes.
        
Once verified, you'll be able to log in and start connecting with other skill sharers!`);
        
        // Redirect to login page
        navigate('/login', { 
          state: { 
            message: 'Registration successful! Please verify your email before logging in.',
            email: formData.email 
          }
        });
      } else {
        // Handle validation errors
        if (data.details && data.details.validation_errors) {
          const errorMessages = Object.entries(data.details.validation_errors)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join('\n');
          alert('Validation errors:\n' + errorMessages);
        } else if (data.errors && Array.isArray(data.errors)) {
          alert('Validation errors:\n' + data.errors.join('\n'));
        } else {
          alert(data.message || 'Registration failed');
        }
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Error connecting to server. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setFormData({
      ...formData,
      [name]: newValue
    });
    
    // Real-time validation for input fields
    if (type !== 'checkbox') {
      setTimeout(() => validateField(name, newValue), 300);
      
      // Special handling for password field
      if (name === 'password') {
        const strength = checkPasswordStrength(newValue);
        setPasswordStrength(strength);
      }
      
      // Special handling for email field
      if (name === 'email' && newValue.includes('@')) {
        setTimeout(() => checkEmailAvailability(newValue), 500);
      }
    }
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
    <div className="auth-container register-enhanced">
      <div className="auth-header">
        <div className="logo-section">
          <div className="skill-icon">🔄</div>
          <h1 className="brand-name">SkillSwap</h1>
        </div>
        <h2 className="auth-title">Create Your Account</h2>
        <p className="auth-subtitle">Join our community and start sharing skills today!</p>
      </div>

      <div className="progress-indicator">
        <div className="progress-step active">
          <div className="step-number">1</div>
          <span>Personal Info</span>
        </div>
        <div className="progress-line"></div>
        <div className="progress-step">
          <div className="step-number">2</div>
          <span>Email Verification</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="auth-form enhanced-form">
        <div className="form-row">
          <div className="form-group full-width">
            <label className="form-label">
              <span className="label-text">Full Name</span>
              <span className="required-star">*</span>
            </label>
            <div className="input-wrapper">
              <div className="input-icon">👤</div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={`form-input ${getFieldClassName('username')}`}
                required
                placeholder="Enter your full name"
              />
            </div>
            {renderFieldErrors('username')}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group full-width">
            <label className="form-label">
              <span className="label-text">Email Address</span>
              <span className="required-star">*</span>
            </label>
            <div className="input-wrapper">
              <div className="input-icon">📧</div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`form-input ${getFieldClassName('email')}`}
                required
                placeholder="Enter your email address"
              />
              {emailChecked && emailAvailable !== null && (
                <div className={`email-status ${emailAvailable ? 'available' : 'unavailable'}`}>
                  {emailAvailable ? '✓ Available' : '✗ Already taken'}
                </div>
              )}
            </div>
            {renderFieldErrors('email')}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group full-width">
            <label className="form-label">
              <span className="label-text">Password</span>
              <span className="required-star">*</span>
            </label>
            <div className="input-wrapper">
              <div className="input-icon">🔒</div>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`form-input ${getFieldClassName('password')}`}
                required
                placeholder="Create a strong password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            
            {formData.password && passwordStrength && (
              <div className="password-strength">
                <div className="strength-bar">
                  <div 
                    className="strength-fill" 
                    style={{ 
                      width: `${(Object.values({
                        length: formData.password.length >= 8,
                        uppercase: /[A-Z]/.test(formData.password),
                        lowercase: /[a-z]/.test(formData.password),
                        number: /\d/.test(formData.password),
                        special: /[!@#$%^&*(),.?":{}|<>]/.test(formData.password)
                      }).filter(Boolean).length / 5) * 100}%`,
                      backgroundColor: passwordStrength.color
                    }}
                  ></div>
                </div>
                <span className="strength-text" style={{ color: passwordStrength.color }}>
                  {passwordStrength.text}
                </span>
              </div>
            )}
            
            {renderFieldErrors('password')}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group full-width">
            <label className="form-label">
              <span className="label-text">Location</span>
              <span className="required-star">*</span>
            </label>
            <div className="input-wrapper">
              <div className="input-icon">📍</div>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                className={`form-input ${getFieldClassName('location')}`}
                required
                placeholder="Enter your city/region"
              />
            </div>
            {renderFieldErrors('location')}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group full-width">
            <div className="checkbox-wrapper">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleChange}
                  className="checkbox-input"
                />
                <span className="checkbox-custom"></span>
                <span className="checkbox-text">
                  Make my profile public so others can find me
                  <small className="checkbox-description">
                    Your skills and location will be visible to other users
                  </small>
                </span>
              </label>
            </div>
          </div>
        </div>

        <button 
          type="submit" 
          className="auth-button primary-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <div className="button-loading">
              <div className="loading-spinner"></div>
              Creating Account...
            </div>
          ) : (
            <>
              <span>Create Account</span>
              <div className="button-icon">🚀</div>
            </>
          )}
        </button>

        <div className="auth-footer">
          <p className="auth-link-text">
            Already have an account? 
            <button 
              type="button" 
              className="link-button"
              onClick={() => navigate('/login')}
            >
              Sign In
            </button>
          </p>
        </div>
      </form>
    </div>
  );
}

export default Register;
