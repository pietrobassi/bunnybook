module.exports = function ({ env: _env }) {
  return {
      babel: {
          plugins: [
              "babel-plugin-transform-typescript-metadata",
              "styled-jsx/babel"
          ]
      },
  };
};