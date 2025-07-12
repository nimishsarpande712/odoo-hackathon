// Frontend validation utilities
import React from 'react';

export class FormValidator {
  static validateName(name) {
    const errors = [];
    
    if (!name || typeof name !== 'string') {
      errors.push('Name is required');
      return { isValid: false, errors };
    }
    
    const trimmedName = name.trim();
    
    if (trimmedName.length < 2) {
      errors.push('Name must be at least 2 characters long');
    }
    
    if (trimmedName.length > 50) {
      errors.push('Name must not exceed 50 characters');
    }
    
    // Only allow letters, spaces, hyphens, and apostrophes
    if (!/^[a-zA-Z\s\-']+$/.test(trimmedName)) {
      errors.push('Name can only contain letters, spaces, hyphens, and apostrophes');
    }
    
    // Check for excessive spaces
    if (/\s{2,}/.test(trimmedName)) {
      errors.push('Name cannot contain multiple consecutive spaces');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      cleanValue: trimmedName
    };
  }
  
  static validateEmail(email) {
    const errors = [];
    
    if (!email || typeof email !== 'string') {
      errors.push('Email is required');
      return { isValid: false, errors };
    }
    
    const trimmedEmail = email.trim().toLowerCase();
    
    // Basic email regex pattern
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (!emailPattern.test(trimmedEmail)) {
      errors.push('Email must be in valid format (e.g., user@example.com)');
    }
    
    // Check for common domains
    const validDomains = ['.com', '.org', '.net', '.edu', '.gov', '.in', '.co'];
    if (!validDomains.some(domain => trimmedEmail.includes(domain))) {
      errors.push('Email must contain a valid domain (e.g., .com, .org, .net)');
    }
    
    if (trimmedEmail.length > 255) {
      errors.push('Email must not exceed 255 characters');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      cleanValue: trimmedEmail
    };
  }
  
  static validatePassword(password) {
    const errors = [];
    
    if (!password || typeof password !== 'string') {
      errors.push('Password is required');
      return { isValid: false, errors };
    }
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    
    if (password.length > 128) {
      errors.push('Password must not exceed 128 characters');
    }
    
    // Check for uppercase letter
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    // Check for lowercase letter
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    // Check for number
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    // Check for special character
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
  
  static validateLocation(location) {
    const errors = [];
    
    if (!location) {
      return { isValid: true, errors: [], cleanValue: '' };
    }
    
    if (typeof location !== 'string') {
      errors.push('Location must be text');
      return { isValid: false, errors };
    }
    
    const trimmedLocation = location.trim();
    
    if (trimmedLocation.length > 255) {
      errors.push('Location must not exceed 255 characters');
    }
    
    // Allow letters, numbers, spaces, commas, periods, hyphens, and parentheses
    if (!/^[a-zA-Z0-9\s,.\-()]+$/.test(trimmedLocation)) {
      errors.push('Location can only contain letters, numbers, spaces, commas, periods, hyphens, and parentheses');
    }
    
    if (trimmedLocation.length > 0 && trimmedLocation.length < 2) {
      errors.push('Location must be at least 2 characters long');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      cleanValue: trimmedLocation
    };
  }
  
  static validateSkillName(skillName) {
    const errors = [];
    
    if (!skillName || typeof skillName !== 'string') {
      errors.push('Skill name is required');
      return { isValid: false, errors };
    }
    
    const trimmedSkill = skillName.trim();
    
    if (trimmedSkill.length < 2) {
      errors.push('Skill name must be at least 2 characters long');
    }
    
    if (trimmedSkill.length > 100) {
      errors.push('Skill name must not exceed 100 characters');
    }
    
    // Allow letters, numbers, spaces, hyphens, periods, plus signs, and hash symbols
    if (!/^[a-zA-Z0-9\s\-.+#]+$/.test(trimmedSkill)) {
      errors.push('Skill name can only contain letters, numbers, spaces, hyphens, periods, plus signs, and hash symbols');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      cleanValue: trimmedSkill
    };
  }
  
  static getPasswordStrength(password) {
    let score = 0;
    const feedback = [];
    
    if (password.length >= 8) score += 1;
    else feedback.push('Add more characters');
    
    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('Add lowercase letters');
    
    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('Add uppercase letters');
    
    if (/\d/.test(password)) score += 1;
    else feedback.push('Add numbers');
    
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;
    else feedback.push('Add special characters');
    
    const strength = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'][score];
    const color = ['#ff4444', '#ff8800', '#ffaa00', '#88cc00', '#00cc44'][score];
    
    return { score, strength, color, feedback };
  }
}

// Real-time validation hook for React
export const useFieldValidation = (value, validator) => {
  const [validation, setValidation] = React.useState({ isValid: true, errors: [] });
  
  React.useEffect(() => {
    if (value !== '') {
      const result = validator(value);
      setValidation(result);
    } else {
      setValidation({ isValid: true, errors: [] });
    }
  }, [value, validator]);
  
  return validation;
};
