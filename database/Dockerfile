FROM postgres:13

# Set environment variables
ENV POSTGRES_USER=hospital_admin
ENV POSTGRES_PASSWORD=secure_password
ENV POSTGRES_DB=hospital_db

# Copy initialization SQL script
COPY init-db.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432
