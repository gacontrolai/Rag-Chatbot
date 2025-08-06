/**
 * Utility functions for handling API errors consistently
 */

/**
 * Extract error message from backend response
 * Backend error format: { error: { code: "...", message: "...", details: {...} } }
 */
export const getErrorMessage = (error) => {
  // Handle network errors
  if (!error.response) {
    return 'Network error. Please check your connection.';
  }

  // Handle HTTP errors with backend error format
  const { data } = error.response;
  
  if (data?.error?.message) {
    return data.error.message;
  }

  // Fallback to HTTP status text
  return error.response.statusText || 'An unexpected error occurred';
};

/**
 * Get error code from backend response
 */
export const getErrorCode = (error) => {
  if (error.response?.data?.error?.code) {
    return error.response.data.error.code;
  }
  return 'UNKNOWN_ERROR';
};

/**
 * Get error details from backend response
 */
export const getErrorDetails = (error) => {
  if (error.response?.data?.error?.details) {
    return error.response.data.error.details;
  }
  return null;
};

/**
 * Check if error is authentication related
 */
export const isAuthError = (error) => {
  const code = getErrorCode(error);
  return code === 'AUTHENTICATION_ERROR' || error.response?.status === 401;
};

/**
 * Check if error is validation related
 */
export const isValidationError = (error) => {
  const code = getErrorCode(error);
  return code === 'VALIDATION_ERROR' || error.response?.status === 400;
};

/**
 * Format error for display to user
 */
export const formatErrorForDisplay = (error) => {
  const message = getErrorMessage(error);
  const code = getErrorCode(error);
  const details = getErrorDetails(error);

  let displayMessage = message;

  // Add validation details if available
  if (isValidationError(error) && details && Array.isArray(details)) {
    const validationMessages = details.map(detail => 
      `${detail.field || detail.loc?.join('.')}: ${detail.msg || detail.message}`
    );
    displayMessage += '\n' + validationMessages.join('\n');
  }

  return {
    message: displayMessage,
    code,
    details
  };
};
