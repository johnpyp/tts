const Files = require("./files");
const Db = require("./db");
const buildLogger = require("./logger");

class Services {
	public logger: any;
	public files: any;
	public db: any;

  constructor(config) {
    this.logger = buildLogger(config.loglevel);
    this.files = new Files(config.filesDir, this.logger);
    this.db = new Db(config.env, config.sqlitePath, this.files, this.logger);
  }
}

module.exports = Services;
