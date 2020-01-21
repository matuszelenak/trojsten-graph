require("webpack");

const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

const webpack_rules = [];

const webpackOption = {
    entry: './graph.js',
    output: {
        filename: 'graph.js',
        path: path.resolve(__dirname, 'dist'),
    },
    optimization: {
        minimizer: [new UglifyJsPlugin()],
    },
    module: {
        rules: webpack_rules
    }
};

let babelLoader = {
    test: /\.js$/,
    exclude: /(node_modules|bower_components|webpack\.config\.js)/,
    use: {
        loader: "babel-loader",
        options: {
            presets: ['@babel/preset-env',
                '@babel/react', {
                    'plugins': ['@babel/plugin-proposal-class-properties']
                }]
        }
    }
};

webpack_rules.push(babelLoader);
module.exports = webpackOption;
