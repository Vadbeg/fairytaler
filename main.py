import uvicorn

from fairytaler.routes import app

if __name__ == "__main__":
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        loop="auto",
        reload=True,
        timeout_keep_alive=1200,
        timeout_graceful_shutdown=1200,
    )
    server = uvicorn.Server(config)

    server.run()
