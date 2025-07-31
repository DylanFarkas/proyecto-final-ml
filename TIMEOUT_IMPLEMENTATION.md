# Implementación de Control de Timeout para Benchmarking

## 📋 Descripción

Se ha implementado un sistema de control de timeout para los scripts de benchmarking que permite al usuario decidir si continuar o cancelar las operaciones cuando toman más tiempo del esperado.

## 🚀 Características Implementadas

### 1. Control de Timeout Interactivo
- **Timeout configurable**: Por defecto 30 segundos, pero puede ajustarse
- **Consulta al usuario**: Cuando se alcanza el timeout, se pregunta al usuario si desea continuar
- **Cancelación segura**: Opción de cancelar la operación de forma controlada
- **Compatibilidad con Windows**: Usa threading en lugar de signals para compatibilidad con Windows

### 2. Archivos Modificados

#### `benchmarking/sentiment_compare.py`
- ✅ Implementado control de timeout
- ✅ Interfaz mejorada con emojis y colores
- ✅ Manejo de errores robusto
- ✅ Gráficos mejorados con valores mostrados

#### `benchmarking/intraday_compare.py`
- ✅ Implementado control de timeout
- ✅ Interfaz mejorada con emojis y colores
- ✅ Manejo de errores robusto
- ✅ Gráficos mejorados con valores mostrados

## 🛠️ Implementación Técnica

### Clase TimeoutManager
```python
class TimeoutManager:
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds
        self.should_continue = True
        self.timer = None
```

**Características:**
- Usa `threading.Timer` para compatibilidad multiplataforma
- Callback automático cuando se alcanza el timeout
- Manejo de interrupciones del usuario
- Limpieza automática de recursos

### Función execute_with_timeout
```python
def execute_with_timeout(func, timeout_seconds=30, *args, **kwargs):
```

**Funcionalidad:**
- Ejecuta cualquier función con control de timeout
- Manejo automático de excepciones
- Limpieza de recursos en caso de error

## 🎯 Uso

### Configuración del Timeout
```python
TIMEOUT_SECONDS = 30  # Configurable al inicio del script
```

### Ejecución
1. El script iniciará el benchmark
2. Si la operación tarda más de 30 segundos, aparecerá un mensaje:
   ```
   ⚠️  ADVERTENCIA: La operación ha tardado más de 30 segundos.
   Esto puede indicar que el proceso está tomando más tiempo del esperado.
   ¿Desea continuar con la ejecución? (s/n):
   ```
3. El usuario puede:
   - Escribir `s` o `si` para continuar
   - Escribir `n` o `no` para cancelar
   - Presionar `Ctrl+C` para interrumpir

## 🎨 Mejoras en la Interfaz

### Mensajes Informativos
- 🚀 Inicio de operaciones
- ⏱️ Información de tiempo
- 💻 Uso de CPU
- ✅ Operaciones exitosas
- ❌ Errores
- 🛑 Cancelaciones
- 📊 Resultados
- 📈 Gráficos

### Gráficos Mejorados
- Colores diferenciados para cada método
- Valores mostrados en barras y puntos
- Mejor legibilidad y presentación
- Títulos descriptivos
- Grid de fondo para mejor lectura

## 🔧 Manejo de Errores

### Tipos de Errores Manejados
1. **KeyboardInterrupt**: Ctrl+C del usuario
2. **EOFError**: Entrada inesperada
3. **Timeout**: Operaciones que tardan demasiado
4. **Excepciones generales**: Errores durante la ejecución

### Respuestas del Sistema
- Mensajes claros y descriptivos
- Limpieza automática de recursos
- Salida controlada del programa
- Logs informativos

## 📊 Ejemplo de Salida

```
============================================================
🔄 INICIANDO BENCHMARKING DE PIPELINES
============================================================
⏱️  Timeout configurado: 30 segundos
📊 Se ejecutarán ambos pipelines (secuencial y paralelo)
============================================================

📈 EJECUTANDO PIPELINE SECUENCIAL...
🚀 Iniciando pipeline secuencial (timeout: 30s)...
✅ Tiempo de ejecución secuencial: 25.45 segundos
💻 Uso de CPU secuencial: 85.2%

🚀 EJECUTANDO PIPELINE PARALELO...
🚀 Iniciando pipeline paralelo (timeout: 30s)...
✅ Tiempo de ejecución paralelo: 15.32 segundos
💻 Uso de CPU paralelo: 92.1%

============================================================
📊 RESUMEN DE COMPARACIÓN:
============================================================
⏱️  Tiempo secuencial: 25.45 segundos
💻 Uso de CPU secuencial: 85.2%
⏱️  Tiempo paralelo: 15.32 segundos
💻 Uso de CPU paralelo: 92.1%
🚀 Mejora de velocidad: 39.8%
✅ El pipeline paralelo es 39.8% más rápido

📈 Generando gráficos comparativos...
✅ Mostrando gráficos...

🎉 ¡Benchmarking completado exitosamente!
```

## 🔄 Configuración Personalizada

Para modificar el timeout por defecto, cambiar la variable:
```python
TIMEOUT_SECONDS = 60  # Para 60 segundos de timeout
```

## 🚨 Notas Importantes

1. **Compatibilidad**: El sistema funciona en Windows, Linux y macOS
2. **Recursos**: Los timers se limpian automáticamente para evitar memory leaks
3. **Interrupciones**: El usuario puede interrumpir en cualquier momento con Ctrl+C
4. **Logs**: Todos los eventos importantes se registran en consola

## 🔮 Futuras Mejoras

- [ ] Configuración de timeout desde argumentos de línea de comandos
- [ ] Logs a archivo opcional
- [ ] Múltiples niveles de timeout (warning, critical)
- [ ] Estimación de tiempo restante
- [ ] Progreso visual durante operaciones largas
