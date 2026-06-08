const { Router } = require("express");
const router = Router();
const ctrl = require("../../controllers/lecturaController");
const { validarLectura } = require("../../middleware/validation");

router.get("/", ctrl.listar);
router.get("/:id", ctrl.obtener);
router.post("/", validarLectura, ctrl.crear);
router.put("/:id", validarLectura, ctrl.actualizar);
router.delete("/:id", ctrl.eliminar);

module.exports = router;
