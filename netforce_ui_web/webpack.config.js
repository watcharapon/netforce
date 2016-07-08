var webpack = require("webpack");

module.exports = {
    entry: './main.jsx',
    output: {
        path: __dirname + '/dist/',
        filename: 'netforce-ui-web.js',
        publicPath: 'http://localhost/'
    },
    module: {
        loaders: [
            {
                test: /\.jsx$/,
                loader: 'jsx-loader?insertPragma=React.DOM&harmony'
            },
            { test: /\.css$/, loader: "style-loader!css-loader" },
            {test: /\.(woff|woff2)(\?v=\d+\.\d+\.\d+)?$/, loader: 'url?limit=10000&mimetype=application/font-woff'},
            {test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, loader: 'url?limit=10000&mimetype=application/octet-stream'},
            {test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, loader: 'file'},
            {test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, loader: 'url?limit=10000&mimetype=image/svg+xml'},
            { test: /\.(png|jpg|gif)$/, loader: 'url-loader?limit=8192' },
        ]
    },
    resolve: {
        extensions: ['', '.js', '.jsx'],
    },
}
