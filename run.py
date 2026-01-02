from app import create_app

app = create_app()

if __name__ == '__main__':
    # use_reloader=False is important to avoid creating two background tracker threads
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
