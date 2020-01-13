const webpack = require('webpack');

module.exports = {
  devServer: {
      disableHostCheck: true
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        'process.env.VUE_APP_API_URL': JSON.stringify(process.env.VUE_APP_API_URL)

      })
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
