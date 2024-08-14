from fastapi import FastAPI
from routes.entry import entry_root
from routes.blog import blog_root
from routes.auth import auth_router  # Import the authentication routes

app = FastAPI()

app.include_router(entry_root, prefix="/auth")
app.include_router(blog_root, prefix="/blog")
app.include_router(auth_router)  # Include the authentication router

# Run the application (if not using uvicorn/gunicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
