FROM python:slim

# Metadata
LABEL maintainer="DSI Factory"
LABEL description="RPA Normalizador de Cuentas"

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 rpauser && \
    mkdir -p /app/out /app/data && \
    chown -R rpauser:rpauser /app

WORKDIR /app

# Copiar solo requirements primero (cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=rpauser:rpauser . .

# Cambiar a usuario no-root
USER rpauser

# Health check (opcional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Comando por defecto
CMD ["python", "-m", "app.main"]