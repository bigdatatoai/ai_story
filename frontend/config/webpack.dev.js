const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'eval-source-map',
  devServer: {
    port: 3002,
    hot: true,
    open: true,
    historyApiFallback: true,
    client: {
      overlay: {
        errors: true,
        warnings: false,
      },
    },
    proxy: [
      {
        context: ['/api'],
        target: 'http://127.0.0.1:8010',
        changeOrigin: true,
        secure: false,
      },
      {
        context: ['/media'],
        target: 'http://127.0.0.1:8010',
        changeOrigin: true,
        secure: false,
      },
    ],
  },
});
