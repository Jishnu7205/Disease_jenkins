# ————————————————————————
# Stage 1: Build with clean Python
# ————————————————————————
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build-time dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy app code and requirements
COPY main.py .
COPY model/ ./model/
COPY models/ ./models/
COPY requirements.txt .

# Install all dependencies into /install
RUN pip install --prefix=/install -r requirements.txt

# Install torch into /install too
RUN pip install --prefix=/install torch==2.7.1 --extra-index-url https://download.pytorch.org/whl/cpu 

# ————————————————————————
# Stage 2: Final lightweight image
# ————————————————————————
FROM python:3.13-slim

WORKDIR /app

# Runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Set paths
ENV PATH="/install/bin:$PATH"
ENV PYTHONPATH="/install/lib/python3.13/site-packages:/app"

# Copy installed packages
COPY --from=builder /install /install
COPY --from=builder /app /app

# Expose port and run server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]