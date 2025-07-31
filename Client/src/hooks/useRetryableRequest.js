import { useState, useCallback, useRef } from 'react';
import { useAlert } from '../contexts/AlertContext';

export const useRetryableRequest = (maxRetries = 3, retryDelay = 1000) => {
  const [loading, setLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const { showError, showWarning } = useAlert();
  const abortControllerRef = useRef(null);

  const executeRequest = useCallback(async (requestFn, options = {}) => {
    const { onSuccess, onError, showSuccessMessage, retryOnError = true } = options;
    
    // Cancelar request anterior si existe
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Crear nuevo AbortController
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    
    const attemptRequest = async (attempt = 0) => {
      try {
        const result = await requestFn({ signal: abortControllerRef.current.signal });
        
        // Reset retry count on success
        setRetryCount(0);
        
        if (showSuccessMessage) {
          showSuccessMessage(result);
        }
        
        if (onSuccess) {
          onSuccess(result);
        }
        
        return result;
      } catch (error) {
        // Si el request fue cancelado, no hacer nada
        if (error.name === 'AbortError') {
          return;
        }
        
        const isLastAttempt = attempt >= maxRetries;
        
        if (!isLastAttempt && retryOnError) {
          setRetryCount(attempt + 1);
          
          if (attempt === 0) {
            showWarning(`Error de conexión. Reintentando... (${attempt + 1}/${maxRetries})`);
          }
          
          // Esperar antes del siguiente intento
          await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
          
          return attemptRequest(attempt + 1);
        } else {
          // Último intento fallido
          setRetryCount(0);
          
          const errorMessage = error.message || 'Error inesperado';
          showError(errorMessage);
          
          if (onError) {
            onError(error);
          }
          
          throw error;
        }
      }
    };
    
    try {
      const result = await attemptRequest();
      return result;
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [maxRetries, retryDelay, showError, showWarning]);

  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setLoading(false);
      setRetryCount(0);
    }
  }, []);

  return {
    loading,
    retryCount,
    executeRequest,
    cancelRequest
  };
};

export default useRetryableRequest;
