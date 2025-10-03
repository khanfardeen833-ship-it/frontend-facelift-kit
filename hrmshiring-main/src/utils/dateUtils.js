/**
 * Date utility functions for consistent DD/MM/YYYY format throughout the application
 */

/**
 * Format a date string or Date object to DD/MM/YYYY format for display
 * @param {string|Date} dateInput - Date string or Date object
 * @returns {string} - Formatted date in DD/MM/YYYY format
 */
export const formatDateForDisplay = (dateInput) => {
  if (!dateInput) return 'Not specified';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) {
      return dateInput.toString();
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
  } catch (error) {
    console.error('Error formatting date for display:', error);
    return dateInput.toString();
  }
};

/**
 * Format a date string or Date object to DD/MM/YYYY format with time
 * @param {string|Date} dateInput - Date string or Date object
 * @param {string} timeInput - Time string (optional)
 * @returns {string} - Formatted date and time in DD/MM/YYYY HH:MM format
 */
export const formatDateTimeForDisplay = (dateInput, timeInput = null) => {
  if (!dateInput) return 'Not specified';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) {
      return dateInput.toString();
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    let formattedDate = `${day}/${month}/${year}`;
    
    if (timeInput) {
      // Format time to HH:MM
      let timeStr = timeInput;
      if (timeStr.includes(':')) {
        const [hours, minutes] = timeStr.split(':');
        timeStr = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
      }
      formattedDate += ` ${timeStr}`;
    }
    
    return formattedDate;
  } catch (error) {
    console.error('Error formatting datetime for display:', error);
    return dateInput.toString();
  }
};

/**
 * Convert DD/MM/YYYY format to YYYY-MM-DD for HTML date input
 * @param {string} ddmmyyyy - Date in DD/MM/YYYY format
 * @returns {string} - Date in YYYY-MM-DD format for HTML input
 */
export const convertDDMMYYYYToHTMLDate = (ddmmyyyy) => {
  if (!ddmmyyyy || !ddmmyyyy.includes('/')) {
    return '';
  }
  
  try {
    const [day, month, year] = ddmmyyyy.split('/');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  } catch (error) {
    console.error('Error converting DD/MM/YYYY to HTML date:', error);
    return '';
  }
};

/**
 * Convert YYYY-MM-DD format to DD/MM/YYYY for display
 * @param {string} yyyymmdd - Date in YYYY-MM-DD format
 * @returns {string} - Date in DD/MM/YYYY format
 */
export const convertHTMLDateToDDMMYYYY = (yyyymmdd) => {
  if (!yyyymmdd || !yyyymmdd.includes('-')) {
    return '';
  }
  
  try {
    const [year, month, day] = yyyymmdd.split('-');
    return `${day}/${month}/${year}`;
  } catch (error) {
    console.error('Error converting HTML date to DD/MM/YYYY:', error);
    return '';
  }
};

/**
 * Format date for input field (converts from DD/MM/YYYY to YYYY-MM-DD for HTML date input)
 * @param {string} dateString - Date string in various formats
 * @returns {string} - Date in YYYY-MM-DD format for HTML input
 */
export const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  
  try {
    // Handle GMT format dates
    if (dateString.includes('GMT')) {
      const date = new Date(dateString);
      return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD
    }
    
    // Handle ISO format dates
    if (dateString.includes('T')) {
      return dateString.split('T')[0];
    }
    
    // Handle DD/MM/YYYY format
    if (dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
      return convertDDMMYYYYToHTMLDate(dateString);
    }
    
    // If it's already in YYYY-MM-DD format
    if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
      return dateString;
    }
    
    // Try to parse as a regular date and convert
    const date = new Date(dateString);
    if (!isNaN(date.getTime())) {
      return date.toISOString().split('T')[0];
    }
    
    return '';
  } catch (error) {
    console.error('Error formatting date for input:', error);
    return '';
  }
};

/**
 * Format date for storage (converts from DD/MM/YYYY to YYYY-MM-DD for MySQL)
 * @param {string} dateString - Date in DD/MM/YYYY format from input
 * @returns {string} - Date in YYYY-MM-DD format for MySQL storage
 */
export const formatDateForStorage = (dateString) => {
  if (!dateString) return '';
  
  try {
    // If it's already in YYYY-MM-DD format, return as is
    if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) {
      return dateString;
    }
    
    // If it's in DD/MM/YYYY format, convert to YYYY-MM-DD
    if (dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
      const [day, month, year] = dateString.split('/');
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    }
    
    // Try to parse as a regular date and convert to YYYY-MM-DD
    const date = new Date(dateString);
    if (!isNaN(date.getTime())) {
      return date.toISOString().split('T')[0];
    }
    
    return '';
  } catch (error) {
    console.error('Error formatting date for storage:', error);
    return '';
  }
};

/**
 * Validate DD/MM/YYYY date format
 * @param {string} dateString - Date string to validate
 * @returns {boolean} - True if valid DD/MM/YYYY format
 */
export const isValidDDMMYYYY = (dateString) => {
  if (!dateString || !dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
    return false;
  }
  
  try {
    const [day, month, year] = dateString.split('/').map(num => parseInt(num, 10));
    const date = new Date(year, month - 1, day);
    
    return date.getDate() === day && 
           date.getMonth() === month - 1 && 
           date.getFullYear() === year;
  } catch (error) {
    return false;
  }
};

/**
 * Get current date in DD/MM/YYYY format
 * @returns {string} - Current date in DD/MM/YYYY format
 */
export const getCurrentDateDDMMYYYY = () => {
  const now = new Date();
  const day = String(now.getDate()).padStart(2, '0');
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const year = now.getFullYear();
  return `${day}/${month}/${year}`;
};

/**
 * Get minimum date for date inputs (today) in YYYY-MM-DD format
 * @returns {string} - Today's date in YYYY-MM-DD format
 */
export const getMinDateForInput = () => {
  return new Date().toISOString().split('T')[0];
};
