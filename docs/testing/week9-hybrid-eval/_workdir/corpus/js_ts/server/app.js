import express from "express";
import { util } from "../pkg/helpers";

const app = express();

function health(_req, res) {
  util(1);
  res.send("ok");
}

app.get("/health", health);

export function boot() {
  app.listen(3000);
}
