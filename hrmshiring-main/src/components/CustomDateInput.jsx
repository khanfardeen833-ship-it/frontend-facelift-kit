import React, { useState, useEffect } from 'react';
import { Calendar } from 'lucide-react';
import { convertDDMMYYYYToHTMLDate, convertHTMLDateToDDMMYYYY, isValidDDMMYYYY } from '../utils/dateUtils';

const CustomDateInput = ({ 
  value, 
  onChange, 
  placeholder = "dd/mm/yyyy", 
  min = null,
  className = "",
  required = false,
  disabled = false
}) => {
  const [displayValue, setDisplayValue] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [showError, setShowError] = useState(false);

  // Initialize display value from HTML date format
  useEffect(() => {
    if (value) {
      const ddmmyyyy = convertHTMLDateToDDMMYYYY(value);
      setDisplayValue(ddmmyyyy);
    } else {
      setDisplayValue('');
    }
  }, [value]);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    setDisplayValue(inputValue);

    // Validate format as user types
    if (inputValue === '') {
      setIsValid(true);
      setShowError(false);
      onChange(''); // Clear the value
      return;
    }

    // Check if it's a valid DD/MM/YYYY format
    const valid = isValidDDMMYYYY(inputValue);
    setIsValid(valid);
    setShowError(!valid && inputValue.length >= 8);

    if (valid) {
      // Convert to HTML date format for storage
      const htmlDate = convertDDMMYYYYToHTMLDate(inputValue);
      onChange(htmlDate);
    }
  };

  const handleKeyDown = (e) => {
    // Allow only numbers, backspace, delete, and forward slash
    const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'];
    const isNumber = e.key >= '0' && e.key <= '9';
    const isSlash = e.key === '/';
    
    if (!isNumber && !isSlash && !allowedKeys.includes(e.key)) {
      e.preventDefault();
    }

    // Auto-format as user types
    if (isNumber) {
      const currentValue = displayValue;
      const cursorPos = e.target.selectionStart;
      
      // Auto-add slashes at appropriate positions
      if (currentValue.length === 2 && cursorPos === 2) {
        setTimeout(() => {
          setDisplayValue(currentValue + '/');
        }, 0);
      } else if (currentValue.length === 5 && cursorPos === 5) {
        setTimeout(() => {
          setDisplayValue(currentValue + '/');
        }, 0);
      }
    }
  };

  const handleBlur = () => {
    if (displayValue && !isValid) {
      setShowError(true);
    }
  };

  const handleFocus = () => {
    setShowError(false);
  };

  return (
    <div className="relative">
      <div className="relative">
        <input
          type="text"
          value={displayValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          onFocus={handleFocus}
          placeholder={placeholder}
          className={`w-full px-3 py-2 pr-10 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
            showError ? 'border-red-300 focus:ring-red-500' : 'border-gray-300'
          } ${className}`}
          maxLength={10}
          required={required}
          disabled={disabled}
        />
        <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
      </div>
      
      {showError && (
        <p className="mt-1 text-sm text-red-600">
          Please enter date in DD/MM/YYYY format
        </p>
      )}
      
      {/* Helper text */}
      <p className="mt-1 text-xs text-gray-500">
        Format: DD/MM/YYYY (e.g., 25/12/2024)
      </p>
    </div>
  );
};

export default CustomDateInput;
