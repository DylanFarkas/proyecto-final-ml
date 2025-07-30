# Manejo de Errores - Documentación

Este documento describe el sistema de manejo de errores implementado en el proyecto, que incluye try-catch tanto en el backend (FastAPI) como en el frontend (React).

## 🔧 Backend - FastAPI

### Características implementadas:

1. **Middleware global de manejo de errores**
   - Captura errores no manejados en toda la aplicación
   - Registra errores con logging para depuración
   - Retorna respuestas JSON consistentes

2. **Validación de parámetros**
   - Validación de formatos de fecha
   - Validación de rangos de fechas
   - Validación de criterios y tipos de datos

3. **Manejo específico por tipo de error**:
   - **400 Bad Request**: Datos inválidos, formatos incorrectos
   - **404 Not Found**: Archivos no encontrados, datos no disponibles
   - **500 Internal Server Error**: Errores internos del servidor

4. **Logging estructurado**
   - Registro de errores con contexto
   - Diferentes niveles de logging (INFO, ERROR)

### Ejemplo de endpoint con manejo de errores:

```python
@router.get("/returns/filter")
def get_filtered_returns(start_date: date, end_date: date):
    try:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")
        
        df = get_cumulative_returns()
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron datos para el rango de fechas especificado")
        
        return JSONResponse(content=df.to_dict(orient="records"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al filtrar retornos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
```

## 🎨 Frontend - React

### Características implementadas:

1. **Sistema de alertas no invasivas**
   - Alertas tipo toast que aparecen en la esquina superior derecha
   - Diferentes tipos: error, success, warning, info
   - Auto-desaparecen después de un tiempo configurable
   - Animaciones suaves de entrada y salida

2. **Contexto global de alertas**
   - Proveedor de contexto `AlertProvider`
   - Hook personalizado `useAlert()`
   - Manejo centralizado de todas las alertas

3. **Hook personalizado para operaciones async**
   - `useAsyncOperation` para manejar estados de carga
   - Manejo automático de errores
   - Integración con el sistema de alertas

4. **Validación en el frontend**
   - Validación de fechas antes de enviar requests
   - Validación de campos requeridos
   - Estados de loading para mejor UX

### Componente Alert:

```jsx
import Alert from '../components/common/Alert';

// Uso en componente
const { showError, showSuccess } = useAlert();

// Mostrar error
showError("Error al cargar datos");

// Mostrar éxito
showSuccess("Datos guardados correctamente");
```

### Hook useAsyncOperation:

```jsx
import useAsyncOperation from '../hooks/useAsyncOperation';

const { loading, executeAsync } = useAsyncOperation();

const handleSubmit = async () => {
  try {
    await executeAsync(
      () => apiCall(),
      "Operación completada con éxito"
    );
  } catch (error) {
    // Error ya manejado por executeAsync
  }
};
```

## 🔄 Flujo de manejo de errores

1. **Request del frontend** → API call con try-catch
2. **Backend procesa** → Validaciones y manejo de errores específicos
3. **Response con error** → HTTP status code + mensaje descriptivo
4. **Frontend recibe error** → Función handleApiError procesa la respuesta
5. **Alerta mostrada** → Sistema de alertas muestra mensaje al usuario

## 📋 Tipos de errores manejados

### Backend:
- Archivos no encontrados
- Formatos de fecha inválidos
- Rangos de fechas incorrectos
- Errores de validación de datos
- Errores de conexión a Ray
- Errores internos del servidor

### Frontend:
- Errores de red (sin conexión)
- Errores del servidor (4xx, 5xx)
- Timeouts
- Errores de validación local

## 🎯 Beneficios

1. **Experiencia de usuario mejorada**
   - Mensajes de error claros y descriptivos
   - Alertas no invasivas
   - Estados de loading apropiados

2. **Depuración más fácil**
   - Logging estructurado en backend
   - Errores específicos por tipo de problema
   - Stack traces para desarrollo

3. **Mantenimiento simplificado**
   - Código centralizado para manejo de errores
   - Patrones consistentes en toda la aplicación
   - Separación de responsabilidades

4. **Robustez de la aplicación**
   - Prevención de crashes inesperados
   - Degradación elegante de funcionalidades
   - Recuperación automática cuando es posible

## 🚀 Implementación en nuevos componentes

Para nuevos componentes, siga este patrón:

```jsx
import { useAlert } from '../contexts/AlertContext';
import useAsyncOperation from '../hooks/useAsyncOperation';

const NuevoComponente = () => {
  const { showError } = useAlert();
  const { loading, executeAsync } = useAsyncOperation();

  const handleAction = async () => {
    try {
      await executeAsync(
        () => nuevaAPICall(),
        "Acción completada"
      );
    } catch (error) {
      // Error manejado automáticamente
    }
  };

  return (
    <button 
      onClick={handleAction} 
      disabled={loading}
    >
      {loading ? "Procesando..." : "Ejecutar"}
    </button>
  );
};
```

## 📝 Notas importantes

- Todos los console.error fueron reemplazados por el sistema de alertas
- Los errores de red muestran mensajes user-friendly
- El sistema es extensible para nuevos tipos de alertas
- Compatible con modo oscuro/claro
- Accesible y responsive
