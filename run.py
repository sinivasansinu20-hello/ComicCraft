import uvicorn

if __name__ == "__main__":
    print("==================================================")
    print(" Starting ComicCraft - AI Comic Creator")
    print(" Open in browser: http://127.0.0.1:8000")
    print("==================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
