from app import init_app

application = init_app()

if __name__ == "__main__":
    application.run(host="localhost", port=8000, debug=False)


