from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import hashlib
import secrets

app = FastAPI(title="XSS Vulnerable App")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory storage
users = {}  # username -> {"password_hash": str, "comments": list}
sessions = {}  # session_id -> username


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect to user profile if logged in, else to login page."""
    session_id = request.cookies.get("session_id")
    if username := sessions.get(session_id):
        return RedirectResponse(f"/user/{username}", status_code=303)
    return RedirectResponse("/login", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(response: Response, username: str = Form(...), password: str = Form(...)):
    """Handle user registration."""
    if username in users:
        return HTMLResponse("Username already exists", status_code=400)

    users[username] = {"password_hash": hash_password(password), "comments": []}
    session_id = secrets.token_hex(16)
    sessions[session_id] = username

    response = RedirectResponse("/login", status_code=303)
    response.set_cookie("session_id", session_id)
    return response


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    """Handle user login."""
    user = users.get(username)
    if not user or user["password_hash"] != hash_password(password):
        return HTMLResponse("Invalid username or password", status_code=401)

    session_id = secrets.token_hex(16)
    sessions[session_id] = username

    response = RedirectResponse(f"/user/{username}", status_code=303)
    response.set_cookie("session_id", session_id)
    response.set_cookie("login", username)  # Intentional vulnerability
    response.set_cookie("password", password)  # Intentional vulnerability
    return response


@app.get("/user/{profile_username}", response_class=HTMLResponse)
async def profile_page(request: Request, profile_username: str):
    """Render user profile page."""
    session_id = request.cookies.get("session_id")
    current_user = sessions.get(session_id)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    if profile_username not in users:
        return HTMLResponse("User not found", status_code=404)

    can_comment = profile_username != current_user
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "current_user": current_user,
        "profile_username": profile_username,
        "comments": users[profile_username]["comments"],
        "user_list": list(users.keys()),
        "can_comment": can_comment
    })


@app.post("/comment/{profile_username}")
async def add_comment(request: Request, profile_username: str):
    """Add comment to user profile (vulnerable to XSS)."""
    session_id = request.cookies.get("session_id")
    current_user = sessions.get(session_id)

    if not current_user or profile_username not in users or profile_username == current_user:
        return {"status": "error", "message": "Cannot comment"}

    data = await request.json()
    text = data.get("text", "")
    if text:
        users[profile_username]["comments"].append(text)
    return {"status": "ok"}

@app.post("/logout")
async def logout(response: Response, request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in sessions:
        del sessions[session_id]
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session_id")
    response.delete_cookie("login")
    response.delete_cookie("password")
    return response


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)