import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import Alert from '../components/common/Alert';

const AlertContext = createContext();

export const useAlert = () => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlert debe ser usado dentro de AlertProvider');
  }
  return context;
};

export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);

  const removeAlert = useCallback((id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  }, []);

  const showAlert = useCallback((message, type = 'error', duration = 5000) => {
    const id = Date.now() + Math.random();
    const newAlert = { id, message, type, duration };
    
    setAlerts(prev => [...prev, newAlert]);

    // Auto remove alert after duration
    setTimeout(() => {
      removeAlert(id);
    }, duration + 300); // Add 300ms for animation
  }, [removeAlert]);

  const showError = useCallback((message, duration) => showAlert(message, 'error', duration), [showAlert]);
  const showSuccess = useCallback((message, duration) => showAlert(message, 'success', duration), [showAlert]);
  const showWarning = useCallback((message, duration) => showAlert(message, 'warning', duration), [showAlert]);
  const showInfo = useCallback((message, duration) => showAlert(message, 'info', duration), [showAlert]);

  const contextValue = useMemo(() => ({
    showAlert, 
    showError, 
    showSuccess, 
    showWarning, 
    showInfo,
    removeAlert 
  }), [showAlert, showError, showSuccess, showWarning, showInfo, removeAlert]);

  return (
    <AlertContext.Provider value={contextValue}>
      {children}
      {alerts.map(alert => (
        <Alert
          key={alert.id}
          message={alert.message}
          type={alert.type}
          duration={alert.duration}
          onClose={() => removeAlert(alert.id)}
        />
      ))}
    </AlertContext.Provider>
  );
};
