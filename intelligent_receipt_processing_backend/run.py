from app import app

if __name__ == "__main__":
    # Bind 0.0.0.0 for containerized execution; default port 3001 to match provided URL
    import os
    port = int(os.environ.get("PORT", "3001"))
    app.run(host="0.0.0.0", port=port)
