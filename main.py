import uvicorn

from fairytaler.routes import app

if __name__ == "__main__":
    config = uvicorn.Config(
        app=app, host="0.0.0.0", port=8000, loop="auto", reload=True
    )
    server = uvicorn.Server(config)

    server.run()
