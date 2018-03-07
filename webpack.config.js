var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  context: __dirname,

  // Each page gets its own bundle
  entry: {
    app: './assets/js/pages/app',
    login: './assets/js/pages/login',
    workflows: './assets/js/pages/workflows.page',
    workflow: './assets/js/pages/workflow.page',
    embed: './assets/js/pages/embed.page'
  },

  output: {
    path: path.resolve('./assets/bundles/'),
    filename: "[name]-[hash].js",
  },
  devtool: 'source-map',
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        // chartbuilder and included modules need their jsx compiled, but most node-modules do not
        exclude: /node_modules(?!([\\]+|\/)(react-tangle|chartbuilder))/,
        loader: 'babel-loader',
        query: {presets: ['env', 'react']}  // to transform JSX into JS
      },
      {
        test: /\.css$/,
        use: [{
          loader: 'style-loader'
        }, {
          loader: 'css-loader'
        }]
      },
      {
        test: /\.scss$/,
        use: [{
          loader: 'style-loader'
        }, {
          loader: 'css-loader'
        }, {
          loader: 'sass-loader'
        }]
      },
      {
        // image handling
        test: /\.(png|jpg|gif)$/,
        loader: 'url-loader',
        options: {
          limit: 25000,
        },
      },
      {
        // font handling
        test: /\.(woff)$/,
        loader: 'url-loader',
        options: {
          limit: 25000,
          mimetype: 'application/font-woff',
          name: '../fonts/[name].[ext]'
        },
      }
    ]
  },

  resolve: {
    modules: ['node_modules'],
    extensions: ['.js', '.jsx']
  },
}
