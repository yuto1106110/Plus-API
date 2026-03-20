from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI(title="YouTube Plus Plus")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# ──────────────────────────────
# カスタムフィルター
# ──────────────────────────────
def duration_filter(seconds):
    if not seconds:
        return ""
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"

def views_filter(count):
    if not count:
        return "0"
    count = int(count)
    if count >= 100000000:
        return f"{count // 100000000}億"
    if count >= 10000:
        return f"{count // 10000}万"
    return f"{count:,}"

templates.env.filters["duration"] = duration_filter
templates.env.filters["views"] = views_filter

# ──────────────────────────────
# ルーター登録
# ──────────────────────────────
app.include_router(pages.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/index")
