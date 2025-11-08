"""
FastAPI application instance and configuration.
Main entry point for the authentication API.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME + " Authentication API",
    version="1.0.0",
    description="Secure user authentication system with email and password",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request object
        exc: Exception that was raised

    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An internal server error occurred" if not settings.DEBUG else str(exc)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} Authentication API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Will add API routes here as they're implemented
# from src.api.routes import auth, password
# app.include_router(auth.router, prefix="/v1")
# app.include_router(password.router, prefix="/v1")
