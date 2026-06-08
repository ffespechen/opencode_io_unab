const mongoose = require("mongoose");

const MONGODB_URI = process.env.MONGODB_URI || "mongodb://iot-mongodb:27017/iot";

async function connectDB() {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log("Conectado a MongoDB:", MONGODB_URI);
  } catch (err) {
    console.error("Error conectando a MongoDB:", err.message);
    process.exit(1);
  }
}

module.exports = connectDB;
