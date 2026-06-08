const express = require("express");
const path = require("path");
const morgan = require("morgan");
const connectDB = require("./config/db");
const apiRoutes = require("./routes/api/lecturas");
const webRoutes = require("./routes/web/lecturas");

const app = express();
const PORT = process.env.PORT || 3000;

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));

app.use(morgan("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api/lecturas", apiRoutes);
app.use("/", webRoutes);

app.use((req, res) => {
  res.status(404).send("Ruta no encontrada");
});

connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://0.0.0.0:${PORT}`);
  });
});
