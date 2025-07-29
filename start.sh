#!/bin/bash

# Build frontend
echo "Building frontend..."
cd frontend
yarn install
yarn build
cd ..

# Start backend API server
echo "Starting backend API server..."
cd backend
python server.py