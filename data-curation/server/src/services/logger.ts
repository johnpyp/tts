import { Logger, TLogLevelName } from "tslog";

export const log: Logger = new Logger({ name: "server" });

export function buildLogger(logLevel: TLogLevelName): Logger {
  return new Logger({
    name: "server",
    minLevel: logLevel,
  });
}
