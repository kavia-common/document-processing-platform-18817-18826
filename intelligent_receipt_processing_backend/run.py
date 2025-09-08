from app import app

if __name__ == "__main__":
    # Bind 0.0.0.0 for containerized execution; default port 3001 to match provided URL
    import os

    # Load environment from .env if present (useful in local/dev and some container runners)
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        # Safe to ignore if python-dotenv not installed; app has sane defaults
        pass

    port = int(os.environ.get("PORT", "3001"))
    app.run(host="0.0.0.0", port=port)
