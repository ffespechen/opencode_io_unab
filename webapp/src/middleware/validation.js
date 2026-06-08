const { body } = require("express-validator");

const validarLectura = [
  body("valor")
    .notEmpty()
    .withMessage("valor es obligatorio")
    .isFloat({ min: -999999, max: 999999 })
    .withMessage("valor debe ser un número decimal"),
  body("sensor")
    .notEmpty()
    .withMessage("sensor es obligatorio")
    .isString()
    .trim()
    .escape(),
  body("ubicacion")
    .notEmpty()
    .withMessage("ubicacion es obligatorio")
    .isString()
    .trim()
    .escape(),
  body("fecha_hora")
    .notEmpty()
    .withMessage("fecha_hora es obligatorio")
    .isISO8601()
    .withMessage("fecha_hora debe ser una fecha ISO8601 válida"),
  body("nodered")
    .notEmpty()
    .withMessage("nodered es obligatorio")
    .isBoolean()
    .withMessage("nodered debe ser true o false"),
];

module.exports = { validarLectura };
