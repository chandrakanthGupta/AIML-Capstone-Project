FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY support_assistant/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directory
COPY support_assistant /app/support_assistant

# Set PYTHONPATH so support_assistant module imports resolve cleanly
ENV PYTHONPATH=/app

# Expose default port
EXPOSE 7860

# Default to graded offline mock mode
ENV MOCK_LLM=1

# Start uvicorn server
CMD ["uvicorn", "support_assistant.src.main:app", "--host", "0.0.0.0", "--port", "7860"]
