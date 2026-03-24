# How to Run the MediVision Frontend

This guide provides step-by-step instructions to set up and run the MediVision frontend web application built with Next.js and React.

## Prerequisites

- Node.js 18 or higher installed on your system
- Git (for cloning the repository if not already done)
- The MediVision backend API running (see main README for backend setup)

## Step 1: Set Up the Project Environment

1. **Clone the Repository** (if not already cloned):
   ```
   git clone <repository-url>
   cd MediVision
   ```

## Step 2: Install Frontend Dependencies

1. **Navigate to Frontend Directory**:
   ```
   cd frontend
   ```

2. **Install Dependencies**:
   ```
   npm install
   ```
   This installs all required Node.js packages for the Next.js application.

## Step 3: Run the Frontend

1. **Start the Development Server**:
   ```
   npm run dev
   ```
   This starts the Next.js development server.

2. **Access the Application**:
   - Open your web browser.
   - Navigate to: `http://localhost:3000/`
   - The MediVision frontend should now load and connect to the backend API.

## Building for Production

To build the application for production:

```
npm run build
npm start
```

This creates an optimized production build and starts the server.

## Troubleshooting

- **Port Conflicts**: If port 3000 is in use, set a different port: `npm run dev -- -p 3001`
- **Backend Connection Issues**: Ensure the backend is running on `http://127.0.0.1:8000/` and the frontend can reach it.
- **Node.js Version Issues**: Ensure you're using Node.js 18 or higher.
- **Permission Errors**: Run terminals as administrator if needed.

## Stopping the Application

- Press `Ctrl+C` in the terminal to stop the development server.

## Development Notes

- The frontend is a single-page application built with Next.js and React.
- It communicates with the Django REST API for data operations.
- For production deployment, consider using Vercel, Netlify, or a custom server setup.