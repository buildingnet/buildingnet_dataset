## three-collada-loader

This is the Three.js Collada loader "extras" package found in the [Three.js source](https://github.com/mrdoob/three.js/blob/master/examples/js/loaders/ColladaLoader.js) ([example](http://threejs.org/examples/#webgl_loader_collada_skinning)).

## Usage:

```js
var ColladaLoader = require('three-collada-loader');

var loader = new ColladaLoader();
loader.load( 'path/to/model.dae', function ( collada ) {
    // Use data here
});
```

See [the offical Three.js documentation](http://threejs.org/docs/#Reference/Loaders/ColladaLoader) for more information and usage.
