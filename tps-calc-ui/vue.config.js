const webpack = require('webpack');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  devServer: {
      disableHostCheck: true
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        'process.env.VUE_APP_API_URL': JSON.stringify(process.env.VUE_APP_API_URL)

      }),
      new CompressionPlugin({
        filename: '[path].br[query]',
        algorithm: 'brotliCompress',
        test: /\.(js|css|html|svg)$/,
        compressionOptions: { level: 11 },
        threshold: 10240,
        minRatio: 0.8,
        deleteOriginalAssets: false,
      }),
    ],
    optimization: {
      runtimeChunk: 'single',
      splitChunks: {
        chunks: 'all'
      }
    }
  },
  pluginOptions: {
    quasar: {
      importStrategy: 'kebab',
      rtlSupport: false,
    },
  },
  transpileDependencies: [
    'quasar',
  ],
};
