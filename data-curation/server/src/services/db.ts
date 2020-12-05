class Db {
	public knex: any;
	public filesService: any;
	public logger: any;

  constructor(env, sqlitePath, filesService, logger) {
    this.knex = require("knex")({
      client: "sqlite3",
      connection: () => ({
        filename: sqlitePath,
        asyncStackTraces: env === "development",
      }),
    });
    this.filesService = filesService;
    this.logger = logger;
  }
}

module.exports = Db;
