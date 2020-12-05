const convict = require("convict");

const config = convict({
  env: {
    doc: "The application environment.",
    format: ["production", "development", "test"],
    default: "development",
    env: "NODE_ENV",
  },
  loglevel: {
    doc: "Log level for loglevel library",
    format: ["error", "warn", "info", "debug", "trace"],
    default: "debug",
    env: "LOGLEVEL",
  },
  sqlitePath: {
    doc: "Sqlite directory",
    format: String,
    default: "./data/sqlite",
    env: "SQLITE_PATH",
  },
  filesDir: {
    doc: "Root directory for managed blobs",
    format: String,
    default: "./data/files",
    env: "FILES_DIR",
  },
});

const env = config.get("env");

config.loadFile(`./config/${env}.json`);

config.validate({ allowed: "strict" });

module.exports = config;
