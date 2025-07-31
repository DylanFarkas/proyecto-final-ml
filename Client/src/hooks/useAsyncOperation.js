import { useState } from 'react';
import { useAlert } from '../contexts/AlertContext';

export const useAsyncOperation = () => {
  const [loading, setLoading] = useState(false);
  const { showError, showSuccess } = useAlert();

  const executeAsync = async (operation, successMessage = null) => {
    setLoading(true);
    try {
      const result = await operation();
      if (successMessage) {
        showSuccess(successMessage);
      }
      return result;
    } catch (error) {
      showError(error.message || 'Ha ocurrido un error inesperado');
      throw error; // Re-throw para que el componente pueda manejar el error si es necesario
    } finally {
      setLoading(false);
    }
  };

  return { loading, executeAsync };
};

export default useAsyncOperation;
