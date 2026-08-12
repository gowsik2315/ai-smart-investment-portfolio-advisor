/**
 * Select Component
 * Reusable dropdown select field
 */

import React from 'react';

const Select = ({ 
  label, 
  name, 
  value, 
  onChange, 
  options = [],
  required = false,
  error = null,
  className = '',
  placeholder = 'Select an option',
  helpText = null,
  ...props 
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-secondary-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        className={`input ${error ? 'border-red-500' : ''}`}
        {...props}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value || option} value={option.value || option}>
            {option.label || option}
          </option>
        ))}
      </select>
      {helpText && !error && (
        <p className="mt-1 text-sm text-secondary-500">{helpText}</p>
      )}
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
};

export default Select;
