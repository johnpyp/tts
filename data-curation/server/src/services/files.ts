import _ from "lodash";
import { dirname, extname, normalize, resolve } from "path";
import fs from "fs-extra";
import { Logger } from "tslog";

class Files {
  public filesDir: string;
  public logger: Logger;

  constructor(filesDir: string, logger: Logger) {
    this.filesDir = filesDir;
    this.logger = logger;
  }
  public async ensureDirs(...dirs: string[]) {
    for (const rawPath of dirs) {
      const isDir = extname(rawPath) === "" || _.endsWith(rawPath, "/");
      const path = resolve(normalize(rawPath));
      const dir = isDir ? dirname(path) : path;
      await fs.ensureDir(dir);
    }
  }
}

module.exports = Files;
