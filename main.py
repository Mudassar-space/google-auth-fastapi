# from fastapi import FastAPI, Request
# from fastapi.responses import RedirectResponse, JSONResponse
# from starlette.middleware.sessions import SessionMiddleware
# from authlib.integrations.starlette_client import OAuth
# from starlette.responses import HTMLResponse
# from dotenv import load_dotenv
# import os

# from database import users_collection
# from models import User

# load_dotenv()

# app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# oauth = OAuth()
# oauth.register(
#     name='google',
#     client_id=os.getenv("GOOGLE_CLIENT_ID"),
#     client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
#     server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#     client_kwargs={'scope': 'openid email profile'}
# )

# @app.get("/", response_class=HTMLResponse)
# async def index():
#     return """
#         <h1>FastAPI Google Signup</h1>
#         <a href='/auth/login'>Login with Google</a>
#     """

# @app.get("/auth/login")
# async def login(request: Request):
#     redirect_uri = request.url_for("auth_callback")
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# @app.get("/auth/callback")
# async def auth_callback(request: Request):
#     try:
#         token = await oauth.google.authorize_access_token(request)
#         user_info = token.get("userinfo")
        
#         # Map to Pydantic model
#         user = User(
#             email=user_info["email"],
#             name=user_info["name"],
#             picture=user_info["picture"],
#             sub=user_info["sub"]
#         )

#         # Check if user exists
#         existing_user = await users_collection.find_one({"sub": user.sub})
#         if not existing_user:
#             await users_collection.insert_one(user.dict())
#             message = "New user signed up successfully!"
#         else:
#             message = "Welcome back!"

#         return JSONResponse(content={"message": message, "user": user.dict()})

#     except Exception as e:
#         print("OAuth error:", e)
#         return JSONResponse(status_code=400, content={"error": str(e)})


















































from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add session middleware for OAuth
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configure OAuth with environment variables
config = Config(environ={
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET")
})

oauth = OAuth(config)

# Register Google OAuth
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Home route with login link
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
        <h1>FastAPI Google OAuth2 Login</h1>
        <a href='/auth/login'>Login with Google</a>
    """

# Login route to redirect to Google's OAuth consent screen
@app.get("/auth/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# Callback route after successful login
@app.get("/auth/callback/")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("OAuth Token:", token)

        user = await oauth.google.parse_id_token(request, token)
        print("Google User:", user)

        return JSONResponse(content={
            "access_token": token["access_token"],
            "user": user
        })
    except Exception as e:
        print("OAuth Error:", str(e))
        return HTMLResponse(f"<h1>OAuth Error</h1><p>{str(e)}</p>", status_code=400)
