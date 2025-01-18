# Base image
FROM postgres:latest

# Set environment variables for PostgreSQL
ENV POSTGRES_USER=deploy
ENV POSTGRES_PASSWORD=VMware123!
ENV POSTGRES_DB=mtg_database

# Create directory for initialization scripts
RUN mkdir -p /docker-entrypoint-initdb.d

# Copy initialization scripts
COPY mtg_schema.sql /docker-entrypoint-initdb.d/

# Set permissions for the scripts
RUN chmod -R 700 /docker-entrypoint-initdb.d

# Expose the default PostgreSQL port
EXPOSE 5432
