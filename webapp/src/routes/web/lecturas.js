const { Router } = require("express");
const router = Router();
const Lectura = require("../../models/lectura");
const { validationResult } = require("express-validator");
const { validarLectura } = require("../../middleware/validation");

router.get("/", async (req, res) => {
  try {
    const docs = await Lectura.find().sort({ fecha_hora: -1 });
    res.render("index", { lecturas: docs, error: null });
  } catch (err) {
    res.render("index", { lecturas: [], error: err.message });
  }
});

router.get("/create", (req, res) => {
  res.render("create", { errors: [], old: {} });
});

router.post("/create", validarLectura, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.render("create", { errors: errors.array(), old: req.body });
  }
  try {
    await Lectura.create(req.body);
    res.redirect("/");
  } catch (err) {
    res.render("create", {
      errors: [{ msg: err.message }],
      old: req.body,
    });
  }
});

router.get("/edit/:id", async (req, res) => {
  try {
    const doc = await Lectura.findById(req.params.id);
    if (!doc) return res.redirect("/");
    res.render("edit", { lectura: doc, errors: [] });
  } catch {
    res.redirect("/");
  }
});

router.post("/edit/:id", validarLectura, async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.render("edit", {
      lectura: { _id: req.params.id, ...req.body },
      errors: errors.array(),
    });
  }
  try {
    await Lectura.findByIdAndUpdate(req.params.id, req.body, {
      runValidators: true,
    });
    res.redirect("/");
  } catch (err) {
    res.render("edit", {
      lectura: { _id: req.params.id, ...req.body },
      errors: [{ msg: err.message }],
    });
  }
});

router.post("/delete/:id", async (req, res) => {
  try {
    await Lectura.findByIdAndDelete(req.params.id);
    res.redirect("/");
  } catch {
    res.redirect("/");
  }
});

module.exports = router;
