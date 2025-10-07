// API configuration
export const getApiConfig = () => {
  // In development, try to get from environment variables
  if (import.meta.env?.DEV) {
    const viteApiUrl = import.meta.env?.VITE_API_URL;
    if (viteApiUrl) {
      return {
        baseUrl: viteApiUrl,
        timeout: 10000,
      };
    }
  }

  // In production or when no env var is set, use relative URLs
  // This allows the frontend to work with the nginx proxy
  return {
    baseUrl: '',
    timeout: 10000,
  };
};

export const API_CONFIG = getApiConfig();