# Multi-stage build for optimized Cloud Run deployment
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve for serving static files
RUN npm install -g serve

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Start the application
CMD ["serve", "-s", "dist", "-l", "8080"]
