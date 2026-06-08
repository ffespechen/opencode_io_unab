const mongoose = require("mongoose");

const lecturaSchema = new mongoose.Schema(
  {
    valor: { type: Number, required: true },
    sensor: { type: String, required: true },
    ubicacion: { type: String, required: true },
    fecha_hora: { type: Date, required: true, default: Date.now },
    nodered: { type: Boolean, required: true },
  },
  { strict: false }
);

module.exports = mongoose.model("Lectura", lecturaSchema, "esp32_lecturas");
