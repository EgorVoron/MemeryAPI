from datetime import datetime
from API.routes import app

if __name__ == "__main__":
    print('Started at', datetime.now())
    app.run(port=8010, host='0.0.0.0')
