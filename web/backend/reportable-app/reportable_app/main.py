import granian
from .bootstrap import create_app

app = create_app()

if __name__ == "__main__":
    granian.Granian(
        "reportable_app.main:app", 
        host="0.0.0.0",
        port=8080,
        reload=True,
        interface="asgi"
    ).serve()