import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://iot-mongodb:27017/iot")
DATABASE_NAME = "iot"
COLLECTION_NAME = "esp32_lecturas"
