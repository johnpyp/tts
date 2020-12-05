module.exports = {
  extends: ["alloy", "alloy/vue", "alloy/typescript"],
  env: {
    browser: true,
    node: true,
  },
  globals: {},
  rules: {
    "max-params": 0,

    "@typescript-eslint/explicit-member-accessibility": [
      "error",
      {
        accessibility: "explicit",
        overrides: {
          accessors: "explicit",
          constructors: "no-public",
          methods: "explicit",
          properties: "explicit",
          parameterProperties: "explicit",
        },
      },
    ],
  },
  parser: "@typescript-eslint/parser",
};
