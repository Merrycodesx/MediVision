FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Run migrations
RUN cd medV_backend && python manage.py migrate

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "medV_backend/manage.py", "runserver", "0.0.0.0:8000"]