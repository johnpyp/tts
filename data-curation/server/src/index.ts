const config = require("./config");
const Services = require("./services");

async function main() {
  const services = new Services(config);
  await services.asyncInit();
}

main();
