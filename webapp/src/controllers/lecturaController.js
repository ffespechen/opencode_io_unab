const Lectura = require("../models/lectura");

exports.listar = async (req, res) => {
  try {
    const filtro = {};
    if (req.query.sensor) filtro.sensor = req.query.sensor;
    if (req.query.ubicacion) filtro.ubicacion = req.query.ubicacion;
    const docs = await Lectura.find(filtro).sort({ fecha_hora: -1 });
    res.json(docs);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.obtener = async (req, res) => {
  try {
    const doc = await Lectura.findById(req.params.id);
    if (!doc) return res.status(404).json({ error: "No encontrado" });
    res.json(doc);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.crear = async (req, res) => {
  try {
    const doc = await Lectura.create(req.body);
    res.status(201).json(doc);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.actualizar = async (req, res) => {
  try {
    const doc = await Lectura.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
      runValidators: true,
    });
    if (!doc) return res.status(404).json({ error: "No encontrado" });
    res.json(doc);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.eliminar = async (req, res) => {
  try {
    const doc = await Lectura.findByIdAndDelete(req.params.id);
    if (!doc) return res.status(404).json({ error: "No encontrado" });
    res.json({ mensaje: "Eliminado correctamente" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
