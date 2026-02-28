# =============================================================================
# DOCKERFILE PARA EL NÚCLEO DE PROMETEO (PROMETEO_CORE)
# =============================================================================
#
# SEGURIDAD POR DISEÑO:
# - Imagen base Debian-slim para permitir instalación de librerías científicas como
#   PyTorch, manteniendo tamaño moderado.
# - Creación de un usuario sin privilegios 'prometeo' para ejecutar el proceso.
# - El sistema de archivos será de solo lectura en tiempo de ejecución.
# - Los volúmenes montados (logs, sandbox) serán las únicas zonas de escritura.
#
# =============================================================================

FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar solo los archivos de dependencias primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar dependencias y herramientas de compilación, luego limpiar
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*

# Crear un usuario y un grupo sin privilegios para ejecutar la aplicación
RUN groupadd -r prometeo && useradd -r -g prometeo prometeo

# Copiar el resto de la aplicación como el usuario no-root
COPY --chown=prometeo:prometeo . .

# Crear los directorios para los volúmenes de escritura
RUN mkdir -p /app/logs /app/sandbox && \
    chown prometeo:prometeo /app/logs /app/sandbox

# Cambiar al usuario sin privilegios
USER prometeo

# Comando por defecto para ejecutar el núcleo de Prometeo
CMD ["python", "prometeo_core.py"]
