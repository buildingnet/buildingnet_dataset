/**
    * Created by rajendrahn on 28/01/16.
    */

var UNSELECTEDOBJTRANSPARENCY = 0.2;
var SELECTEDOBJTRANSPARENCY = 0.8;
var DEFAULTANIMATIONSPEED = 0.01;
var greycolor = ['DCDCDC','D3D3D3','C0C0C0','A9A9A9','808080','696969','778899','708090']
function CameraSetUp(position, lookAt, rotation) {
    this.position = position;
    this.lookAt = lookAt;
    this.rotation = rotation;
}

function Frame(top, left, width, height) {
    this.top = top;
    this.left = left;
    this.width = width;
    this.height = height;
}


function View(container, frame) {
    this.container = container;
    this.frame = frame;
    this.canvas = null;
    this.canvasposition = null;
    this.scene = new THREE.Scene();
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.rootObj = null;
    this.objs = [];
    this.objcolor = {};
    this.objnames = [];
    this.selectedObjs = [];
    this.expandshrinkSelected = [];
    this.current_filename = null;
    this.isAnimating = false;
    this.isLoadingMesh = false;
    this.animationSpeed = DEFAULTANIMATIONSPEED;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.cameraInfo = null;
    this.similarObjectsData = null;
    this.objtocamera = null;
    this.keysPressed = [];
    this.lookAt = null;
    this.onSelect = null;
    this.objIdtoChildId = {};
    this.childIdtoObjId = {};
    this.childIdToObj = {};
    this.childIdToParents = {};
    this.parentIdToChildId = {};
    this.parentchildobjstoUnselect = [];

    this.colors = [];
    this.camindex = 0;
    this.cameraPositions = [];
    //this.interior = [];
    this.visibleindices = [];
    this.center = null;
    this.initialCenter = null;
    this.totalobjects = 0;
    this.radius = 0;
    this.exterior = 0;
    this.surfacearea = [];

    this.hierarchy = {};

//    this.level = {};
//    this.parentlevel = {};
    this.currentlevel = {};

    THREE.Loader.Handlers.add( /\.dds$/i, new THREE.DDSLoader());
    this.initLights();
    this.initCamera();
    this.initRenderer();
    this.initControls();
    this.initColors();
    this.initCenter();
}

View.prototype.updateCamera = function() {
    this.camera.up.set(0,1,0);
//    console.log(this.center);
    this.camera.position.set(this.center.getComponent(0) + 1.5* this.radius , this.center.getComponent(1), this.center.getComponent(2));
    
//    console.log(this.camera.position);
    this.camera.lookAt(this.center);

    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld();
}

View.prototype.initCamera = function() {
//    //console.log("initiating camera");
    this.camera = new THREE.PerspectiveCamera(70, this.frame.width/this.frame.height, 0.01, 100000000);
    this.camera.position.set(0,0, 1);

    this.camera.lookAt(this.scene.position);
//    console.log(this.camera.up);
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld();
//    console.log(this.camera.up);
    console.log(this.camera);
};

View.prototype.resetCamera = function(){
    this.camera.position.set(0,0,1);
    this.camera.up.set(0,1,0);
    this.camera.lookAt(this.scene.position);
//    console.log(this.camera.up);
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld();
//    console.log(this.camera.up);
}


View.prototype.initCenter = function() {
    this.center = new THREE.Vector3();
}

View.prototype.initLights = function() {
    var light = new THREE.AmbientLight(0xffffff);
    this.scene.add(light);

    var directionalLight = new THREE.DirectionalLight( 0x646464 );
    directionalLight.position.set( 0, 0, 1 ).normalize();
    this.scene.add( directionalLight );
};

View.prototype.initRenderer = function() {
    
    this.renderer = new THREE.WebGLRenderer({antialias: true});
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.setSize(this.frame.width, this.frame.height);
    this.container.appendChild(this.renderer.domElement);
    this.canvas = this.renderer.domElement;
    this.canvasposition = $(this.canvas).position();
};

View.prototype.initControls = function() {
    this.controls = new THREE.TrackballControls(this.camera, this.renderer.domElement);

    this.controls.rotateSpeed = 3.0;
    this.controls.zoomSpeed = 1.0;
    this.controls.panSpeed = 3.0;
    this.controls.noZoom = false;
    this.controls.noPan = false;
    this.controls.staticMoving = true;
    this.controls.dynamicDampingFactor = 0.3;
    this.controls.keys = [ 65, 83, 18 ];
    this.controls.enabled = !this.isAnimating;
    this.controls.minDistance = 0;
    //this.controls.maxDistance = 3000;

};

View.prototype.initColors = function() {
    //var YlGn = colorbrewer['YlGn'][9];
    this.colors = (this.colors).concat(colorbrewer['Yellow'][20]);
    //var YlGnBu = colorbrewer['YlGnBu'][9];
    //this.colors = (this.colors).concat(YlGnBu);
}

View.prototype.getBoundingBoxScene = function() {
    var minv = new THREE.Vector3(0,0,0);
    var maxv = new THREE.Vector3(0,0,0);
    for(var i=0; i< this.objs.length; i++) {
     //if(!this.interior.includes(this.objs[i].name)){
        var bbox = new THREE.Box3().setFromObject(this.objs[i]);
        minv.x = Math.min(minv.x, bbox.min.x);
        minv.y = Math.min(minv.y, bbox.min.y);
        minv.z = Math.min(minv.z, bbox.min.z);
        maxv.x = Math.max(maxv.x, bbox.max.x);
        maxv.y = Math.max(maxv.y, bbox.max.y);
        maxv.z = Math.max(maxv.z, bbox.max.z);
    // }
   }
   var radius = minv.distanceTo(maxv)/2.0;
   minv.add(maxv);
   minv.divideScalar(2);
   this.center = minv;
   this.initialCenter = minv;
   this.radius  = radius;
}

//View.prototype.changetextureMaterialColor = function() {

//    for(var i=0; i<this.objs.length; i++)
//    {
//        if(this.interior.includes(this.objs[i].name)){
//                this.objs[i].material = new THREE.MeshPhongMaterial({
//                color: '#ff0000',
//                specular: 0x141414,
//                shininess: 20,
//                flatShading: true,
//                transparent: true,
//                //side : THREE.DoubleSide,
//                opacity: 0.0
//
//            });
//        }
        //this.objs[i].material.side = THREE.DoubleSide;
//    }
//}

View.prototype.changeMaterialColor = function() {

    for(var i=0; i<this.objs.length; i++)
    {
//        if(this.interior.includes(this.objs[i].name)){
//                this.objs[i].material = new THREE.MeshPhongMaterial({
//                color: '#ff0000',
//                specular: 0x141414,
//                shininess: 20,
//                flatShading: true,
//                transparent: true,
//                //side : THREE.DoubleSide,
//                opacity: 0.0
//
//            });
//        } else {
            this.objs[i].material = new THREE.MeshPhongMaterial({
                color: this.objcolor[this.objs[i].name],
                specular: 0x141414,
                shininess: 20,
                //side: THREE.DoubleSide,
                flatShading: true
            });
//        }
     this.objs[i].material.side = THREE.DoubleSide;
    }
}


//********* Rendering  **********//

function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

function initLoadingManager() {
//  console.log("init loading manager")
  const manager = new THREE.LoadingManager();
  const progressBar = document.querySelector( '#progress' );
  const loadingOverlay = document.querySelector( '#loading-overlay' );

  let percentComplete = 1;
  let frameID = null;

  const updateAmount = 0.5; // in percent of bar width, should divide 100 evenly

  const animateBar = () => {
    percentComplete += updateAmount;

    // if the bar fills up, just reset it.
    // I'm changing the color only once, you 
    // could get fancy here and set up the colour to get "redder" every time
    if ( percentComplete >= 100 ) {
      
      progressBar.style.backgroundColor = 'blue'
      percentComplete = 1;

    }

    progressBar.style.width = percentComplete + '%';

    frameID = requestAnimationFrame( animateBar )

  }

  manager.onStart = () => {

    // prevent the timer being set again
    // if onStart is called multiple times
    if ( frameID !== null ) return;

    animateBar();

  };

  manager.onLoad = function ( ) {
    sleep(3000);
    loadingOverlay.classList.add( 'loading-overlay-hidden' );

    // reset the bar in case we need to use it again
    percentComplete = 0;
    progressBar.style.width = 0;
    cancelAnimationFrame( frameID );

  };
  
  manager.onError = function ( e ) { 
    
    console.error( e ); 
    
    progressBar.style.backgroundColor = 'red';
  
  }
  
  return manager;
}


View.prototype.render = function () {
    this.animate();
    this.controlupdate();
    this.renderer.render(this.scene, this.camera);
};

View.prototype.controlupdate = function () {
    this.controls.update();
    TWEEN.update();
};


View.prototype.animate = function () {
    if (!this.rootObj || !this.isAnimating) return;
    this.rootObj.rotation.y -= this.animationSpeed;
    //if (!this.scene || !this.isAnimating) return;
    //    this.scene.rotation.y -= this.animationSpeed;
    // for(var i=0; i < this.objs[i].length; i++)
    //    this.objs[i].rotation.y -= this.animationSpeed;
};

View.prototype.colorObjectAtIndices = function(color, indices, resetSelection=true) {
    var hexcolor = (color.toString()).slice(1,);
    for (var i = 0; i < indices.length; i++) {
        this.objs[indices[i]].material.color.setHex('0x'+hexcolor);// .setRGB(color.r, color.g, color.b);
    }

    for(var i =0; i<this.objs.length; i++){
        //if(!(this.interior.includes(this.objs[i].name))){
		if((this.objs[i].material.color).getHexString() == "ff0000"){
		    this.objs[i].material.color.setHex('0x'+(this.objcolor[this.objs[i].name]).substring(1,));
		}
		this.objs[i].material.opacity = 1.0;
		this.objs[i].material.transparent = false;
        //}
    }
    if(resetSelection)
        this.selectedObjs = [];
};

View.prototype.showMesh = function (filename, completionHandler) {
    
    if (this.isLoadingMesh || (this.current_filename != null && this.current_filename == filename)) return;
    this.isLoadingMesh = true;
    this.current_filename = filename;
 
    var manager = initLoadingManager();

    if (this.rootObj != null) {
        this.scene.remove(this.rootObj);
    }

    var thisPointer = this;

    this.similarObjectsData = null;
    $.getJSON("js/similar/" + filename + "_pycollada_similar.json", function(data) {
        thisPointer.similarObjectsData = data;
    });


    this.objtocamera = [];
    $.getJSON("js/objtocamera/" + filename + "_pycollada_objtocamera.json", function(data) {
        thisPointer.objtocamera = data;
    });    

    this.surfacearea= [];
    $.getJSON("js/surfacearea/" + filename + "_pycollada_surfacearea.json", function(data) {
        thisPointer.surfacearea = data;
    });    

    this.hierarchy= [];
    $.getJSON("js/hierarchy/" + filename + "_pycollada_hierarchy.json", function(data) {
        thisPointer.hierarchy = data;
    });

    var mtlLoader = new THREE.MTLLoader();
    mtlLoader.setBaseUrl('js/meshes/');
    mtlLoader.setPath('js/meshes/');
    var url = filename+'.mtl'
    mtlLoader.load(url, function(materials) {
        materials.preload();
        var objLoader = new THREE.OBJLoader();
        objLoader.setMaterials(materials);
        objLoader.setPath('js/meshes/');
        objLoader.load( filename+'.obj', function( object) {
            scene.add(object)
        }, onProgress, onError);
    });

//    var colladaloader = new THREE.ColladaLoader(manager);
//    colladaloader.load('js/meshes/'+filename+'.dae', function(collada) {
//
//        const obj = collada.scene;
//        thisPointer.rootObj = collada.scene;
//        var index = 0;
//         
//        thisPointer.rootObj.traverse(function(child) {
//            if (child instanceof THREE.Mesh) {
//              if(child.visible === false){
//                    console.log("child is not visible");
//                }
//                if(Object.keys(child.geometry.attributes) == 0){
//                   console.log("not a valid geometry")
//                }
//                else {
//
//                c = child;
//                thisPointer.objnames.push(child.name);
//                //thisPointer.objIdtoChildId[index] = (child.id);
//                //thisPointer.childIdtoObjId[child.id] = index;
//
//                child.name = index.toString();
//                thisPointer.currentlevel[child.name] = -1;
//                index++;
//                child.frustumCulled = false;
//                child.material.side = THREE.DoubleSide;
//                var material = child.material;
//		if(child.material && (child.material.color) && ((child.material.color).getHexString() == "ffffff")){
//                    var color = this.greycolor[Math.floor(Math.random() * this.greycolor.length)];
//		    child.material.color.setHex('0x'+color);
//                }
//                thisPointer.objs.push(child);
//                }
//            }
//
//        });
//
//         var randomfacecenters = {};
//          for(i=0; i<thisPointer.objs.length; i++){
//            rfaces = Array();
//            var geometry = new THREE.Geometry().fromBufferGeometry(thisPointer.objs[i].geometry);
//            geometry.vertices.map(x => x.applyMatrix4(thisPointer.objs[i].matrixWorld));
//            for(j=0; j<1; j++){
//                rfaces.push(geometry.faces[Math.floor(Math.random()*Math.floor(geometry.faces.length))]);
//            }
//            randomfacecenters[i] = Array();
//
//            for(j=0; j<1; j++) {
//                v0 = geometry.vertices[rfaces[j].a]
//                v1 = geometry.vertices[rfaces[j].b]
//                v2 = geometry.vertices[rfaces[j].c]
//                centroid = new THREE.Vector3((v0.x+v1.x+v2.x)/3, (v0.y+v1.y+v2.y)/3, (v0.z+v1.z+v2.z)/3);
//                randomfacecenters[i].push(centroid);
//            }
//          }
//
////       var posx = [[-0.96622826,  0.08014163,  0.24490871],
////       [-0.75746757,  0.65278191, -0.01089258],
////       [ 0.27291806,  0.95925497, -0.07311388],
////       [-0.25705575,  0.28538426,  0.92329744],
////       [ 0.81400034,  0.05539942, -0.57821652],
////       [-0.67885315,  0.71756655, -0.15574543],
////       [-0.98802444,  0.06784167, -0.13858288],
////       [-0.10271159,  0.67235947, -0.73306417],
////       [ 0.56305807,  0.47613215, -0.67547301],
////       [-0.62943867,  0.648595  ,  0.42793864],
////       [-0.75897936,  0.0155035 , -0.65093008],
////       [ 0.40646431,  0.37166432, -0.83465705],
////       [-0.80741289,  0.2307706 ,  0.54298191],
////       [-0.55769537,  0.73170177,  0.39190356],
////       [-0.15687362,  0.26565041, -0.95122055],
////       [-0.4590404 ,  0.88402024, -0.08826166],
////       [-0.37066533,  0.46203793, -0.80568491],
////       [ 0.862822  ,  0.33624893,  0.37745842],
////       [-0.17971372,  0.68876624, -0.70235607],
////       [ 0.4960879 ,  0.00937637, -0.86822168],
////       [-0.92872284,  0.2246228 , -0.29498895],
////       [ 0.97086474,  0.06907937, -0.22945523],
////       [-0.2850292 ,  0.05489923,  0.95694536],
////       [-0.65413057,  0.67555662, -0.3402006 ],
////       [-0.32992835,  0.72887756,  0.59990398]];
////
////
////
////       var posy = [[-0.08013719, -0.24490901, -0.96622855],
////       [-0.65277917,  0.01089018, -0.75746997],
////       [-0.95925624,  0.07311036,  0.27291454],
////       [-0.28537993, -0.92329849, -0.2570568 ],
////       [-0.05540453,  0.57821632,  0.81400014],
////       [-0.71756463,  0.1557428 , -0.67885579],
////       [-0.06783855,  0.13858263, -0.98802469],
////       [-0.67236178,  0.7330617 , -0.10271406],
////       [-0.4761367 ,  0.67547126,  0.56305632],
////       [-0.64859112, -0.42794103, -0.62944105],
////       [-0.0155031 ,  0.65093003, -0.75897942],
////       [-0.37166888,  0.83465569,  0.40646295],
////       [-0.23076564, -0.54298276, -0.80741374],
////       [-0.73169828, -0.39190625, -0.55769805],
////       [-0.26565332,  0.95121957, -0.15687459],
////       [-0.88401888,  0.08825842, -0.45904365],
////       [-0.46203952,  0.80568321, -0.37066703],
////       [-0.33625071, -0.37745966,  0.86282076],
////       [-0.68876816,  0.70235354, -0.17971625],
////       [-0.00938138,  0.86822164,  0.49608786],
////       [-0.22462047,  0.29498812, -0.92872367],
////       [-0.06908378,  0.22945498,  0.97086448],
////       [-0.05489467, -0.95694557, -0.2850294 ],
////       [-0.67555547,  0.34019812, -0.65413305],
////       [-0.72887414, -0.59990666, -0.32993103]];
////
////
////       var posz = [[-0.24490546,  0.96622916,  0.08014074],
////       [ 0.01089296,  0.75746753,  0.65278195],
////       [ 0.07310935, -0.27291833,  0.95925524],
////       [-0.92329754,  0.25705915,  0.28538087],
////       [ 0.57821333, -0.81400247,  0.05540154],
////       [ 0.15574529,  0.67885258,  0.71756712],
////       [ 0.13858626,  0.98802393,  0.06784218],
////       [ 0.73306208,  0.1027089 ,  0.67236216],
////       [ 0.67546919, -0.56306055,  0.47613464],
////       [-0.42793872,  0.62944024,  0.64859343],
////       [ 0.65093281,  0.75897697,  0.01550589],
////       [ 0.83465419, -0.40646738,  0.37166739],
////       [-0.54297979,  0.80741489,  0.2307686 ],
////       [-0.3919042 ,  0.55769681,  0.73170033],
////       [ 0.95122015,  0.15687012,  0.2656539 ],
////       [ 0.0882601 ,  0.45904008,  0.88402057],
////       [ 0.80568457,  0.37066237,  0.46204089],
////       [-0.37746283, -0.86282061,  0.33624754],
////       [ 0.7023542 ,  0.17971114,  0.68876882],
////       [ 0.86821982, -0.49609109,  0.00937956],
////       [ 0.29499153,  0.92872176,  0.22462388],
////       [ 0.22945141, -0.97086558,  0.06908022],
////       [-0.95694452,  0.28503271,  0.05489572],
////       [ 0.34020052,  0.65412932,  0.67555787],
////       [-0.59990545,  0.32993056,  0.72887535]];
////
////      var posxcircle = [[ 1.00000000e+00,  0.00000000e+00,  0.00000000e+00],
////       [ 9.68583161e-01,  1.52278637e-17, -2.48689887e-01],
////       [ 8.76306680e-01,  2.94989047e-17, -4.81753674e-01],
////       [ 7.28968627e-01,  4.19164211e-17, -6.84547106e-01],
////       [ 5.35826795e-01,  5.17001746e-17, -8.44327926e-01],
////       [ 3.09016994e-01,  5.82354159e-17, -9.51056516e-01],
////       [ 6.27905195e-02,  6.11115119e-17, -9.98026728e-01],
////       [-1.87381315e-01,  6.01477469e-17, -9.82287251e-01],
////       [-4.25779292e-01,  5.54046777e-17, -9.04827052e-01],
////       [-6.37423990e-01,  4.71803288e-17, -7.70513243e-01],
////       [-8.09016994e-01,  3.59914664e-17, -5.87785252e-01],
////       [-9.29776486e-01,  2.25411278e-17, -3.68124553e-01],
////       [-9.92114701e-01,  7.67444717e-18, -1.25333234e-01],
////       [-9.92114701e-01, -7.67444717e-18,  1.25333234e-01],
////       [-9.29776486e-01, -2.25411278e-17,  3.68124553e-01],
////       [-8.09016994e-01, -3.59914664e-17,  5.87785252e-01],
////       [-6.37423990e-01, -4.71803288e-17,  7.70513243e-01],
////       [-4.25779292e-01, -5.54046777e-17,  9.04827052e-01],
////       [-1.87381315e-01, -6.01477469e-17,  9.82287251e-01],
////       [ 6.27905195e-02, -6.11115119e-17,  9.98026728e-01],
////       [ 3.09016994e-01, -5.82354159e-17,  9.51056516e-01],
////       [ 5.35826795e-01, -5.17001746e-17,  8.44327926e-01],
////       [ 7.28968627e-01, -4.19164211e-17,  6.84547106e-01],
////       [ 8.76306680e-01, -2.94989047e-17,  4.81753674e-01],
////       [ 9.68583161e-01, -1.52278637e-17,  2.48689887e-01]];
////
////      var posx_100_dome = [[-0.12651623,  0.4979334 ,  0.85793705],
////       [-0.58981466,  0.77820487, -0.21567531],
////       [ 0.67457803,  0.27845612,  0.68367147],
////       [-0.08411071,  0.26239743,  0.96128715],
////       [-0.81833185,  0.38708017,  0.42485518],
////       [ 0.82198547,  0.56941927, -0.01007857],
////       [ 0.289182  ,  0.95592376, -0.05082847],
////       [ 0.2480719 ,  0.1617954 ,  0.95513485],
////       [ 0.15943503,  0.42374777,  0.89163799],
////       [-0.57300294,  0.343495  , -0.74409597],
////       [-0.74659125,  0.08096253,  0.66033822],
////       [-0.63856512,  0.33545231,  0.69260835],
////       [-0.9078001 ,  0.33735725,  0.24917679],
////       [-0.82200937,  0.55463279,  0.12916297],
////       [-0.05076366,  0.80506487,  0.59101067],
////       [-0.66548924,  0.70686298,  0.23972652],
////       [ 0.22356053,  0.81035852,  0.5416085 ],
////       [ 0.05566614,  0.79107225,  0.60918468],
////       [-0.30701582,  0.37925464,  0.87287296],
////       [-0.96194907,  0.23382046,  0.14135763],
////       [-0.36986523,  0.88426057,  0.28510165],
////       [-0.68712312,  0.718867  , -0.10531881],
////       [ 0.47069379,  0.30302985, -0.82862553],
////       [-0.79986068,  0.49258252, -0.34290721],
////       [-0.35705081,  0.24581767,  0.90115947],
////       [-0.69630507,  0.71772136,  0.00594155],
////       [-0.3605929 ,  0.5370248 ,  0.76261204],
////       [-0.21546847,  0.88061232,  0.42201336],
////       [ 0.92544218,  0.00684501,  0.37882704],
////       [-0.45825707,  0.88365821,  0.09564849],
////       [-0.97472136,  0.13819275,  0.17555919],
////       [-0.44234259,  0.05283035, -0.89528877],
////       [ 0.73544919,  0.45085808, -0.50580776],
////       [ 0.36789715,  0.3929261 ,  0.8427697 ],
////       [-0.4659106 ,  0.19532822, -0.86300301],
////       [ 0.48369559,  0.72329385,  0.49283322],
////       [ 0.53475847,  0.79893273,  0.27520878],
////       [ 0.21934473,  0.76749086, -0.60236673],
////       [-0.60261292,  0.15490798,  0.78285451],
////       [ 0.93450199,  0.2582999 ,  0.24492282],
////       [-0.06834997,  0.55595725, -0.82839593],
////       [ 0.08733304,  0.99303842, -0.07904205],
////       [-0.5799008 ,  0.29501804, -0.75939411],
////       [ 0.42475239,  0.53909037,  0.72730116],
////       [ 0.13157974,  0.3099304 ,  0.94161028],
////       [ 0.82804932,  0.24783773, -0.50290236],
////       [-0.67179893,  0.20554682,  0.71164366],
////       [ 0.82548692,  0.45400669,  0.33533456],
////       [-0.83169685,  0.00873463, -0.55516129],
////       [-0.80258992,  0.51729122,  0.29708451],
////       [ 0.97182047,  0.04068209,  0.23218513],
////       [-0.5473501 ,  0.54163115,  0.63799965],
////       [ 0.62759026,  0.6498534 ,  0.42874354],
////       [ 0.77326462,  0.2030334 ,  0.60069898],
////       [ 0.59120928,  0.40696703, -0.69631129],
////       [ 0.74411254,  0.30237129,  0.5957081 ],
////       [-0.64309234,  0.20333698,  0.73829961],
////       [ 0.93575709,  0.33146538, -0.12037182],
////       [-0.16989634,  0.96468013,  0.20131439],
////       [-0.68215643,  0.56056111, -0.46950384],
////       [ 0.39571843,  0.78498968,  0.47665305],
////       [ 0.47807987,  0.06909338, -0.87559451],
////       [ 0.24411059,  0.27090698,  0.93113878],
////       [-0.03459079,  0.61514763,  0.78765276],
////       [ 0.49014288,  0.08068082, -0.86790009],
////       [-0.7860396 ,  0.50174254,  0.3611041 ],
////       [ 0.66650287,  0.03410136,  0.74472211],
////       [-0.17073385,  0.23190629,  0.95763742],
////       [ 0.58901328,  0.68384043, -0.43061076],
////       [ 0.40453165,  0.54867506, -0.7316487 ],
////       [-0.92289247,  0.17453254, -0.34323153],
////       [ 0.1386954 ,  0.9719949 ,  0.18970898],
////       [ 0.98232325,  0.02500514, -0.1855149 ],
////       [-0.98022914,  0.19578814,  0.02859785],
////       [ 0.05864788,  0.45823286, -0.88689519],
////       [-0.7031926 ,  0.25266233, -0.66459154],
////       [ 0.71607541,  0.19213933,  0.67105774],
////       [-0.80118008,  0.4015752 ,  0.44367537],
////       [ 0.58682243,  0.64454786,  0.49009946],
////       [ 0.39705935,  0.86542601, -0.30558418],
////       [-0.43271626,  0.22213962,  0.87373373],
////       [-0.90672001,  0.22683224,  0.35553616],
////       [ 0.00296812,  0.92176974, -0.38772636],
////       [-0.40076743,  0.04336848,  0.9151528 ],
////       [-0.4291404 ,  0.76672012, -0.47747124],
////       [ 0.13296356,  0.66941527,  0.73089253],
////       [-0.76429941,  0.60018746, -0.23584196],
////       [-0.25965147,  0.94035785,  0.21979131],
////       [ 0.90545956,  0.27885732, -0.31997121],
////       [-0.02788398,  0.89047114,  0.45418458],
////       [-0.85566488,  0.5011241 , -0.12927585],
////       [-0.81833421,  0.30245526, -0.48872277],
////       [ 0.85185957,  0.28024814,  0.44248871],
////       [ 0.63145589,  0.36804069, -0.68250239],
////       [ 0.2158768 ,  0.29324082,  0.93134689],
////       [-0.02726332,  0.68852607, -0.72469894],
////       [-0.58496907,  0.14335889, -0.7982853 ],
////       [ 0.92244829,  0.26608759,  0.27979732],
////       [ 0.80767893,  0.5796299 ,  0.10809217],
////       [ 0.40209788,  0.5330273 ,  0.74444556]];
////
////   var posx_50_dome = [[-0.93987878,  0.18796036,  0.28512942],
////           [-0.87511583,  0.34742646, -0.33684883],
////           [-0.74458075,  0.606031  , -0.2798677 ],
////           [-0.09593704,  0.82255474, -0.56053526],
////           [-0.21367701,  0.92676883, -0.30893636],
////           [-0.73469052,  0.50352023,  0.45463966],
////           [-0.11838046,  0.85444512, -0.50587509],
////           [-0.11354761,  0.93134175,  0.34599057],
////           [-0.75828233,  0.62090715, -0.19870133],
////           [ 0.03135211,  0.26265714, -0.96437973],
////           [-0.81057764,  0.58462095,  0.03438361],
////           [-0.7979256 ,  0.53886813, -0.27006642],
////           [-0.92969349,  0.02685655,  0.36735371],
////           [ 0.01746773,  0.33090738, -0.94350156],
////           [ 0.85440131,  0.51946464,  0.0124455 ],
////           [ 0.33266149,  0.2712948 ,  0.90318075],
////           [ 0.23269776,  0.97248891, -0.01082006],
////           [ 0.3076571 ,  0.30799637,  0.9002696 ],
////           [-0.83059935,  0.47188807, -0.29567952],
////           [ 0.76987184,  0.63744972,  0.03090617],
////           [ 0.82894954,  0.1199042 , -0.54632009],
////           [-0.26827361,  0.96234523, -0.04382847],
////           [-0.11850437,  0.62297759,  0.77321125],
////           [ 0.14906361,  0.42985996, -0.89050573],
////           [-0.41672931,  0.38581518, -0.82309375],
////           [-0.8444835 ,  0.3800255 , -0.37739665],
////           [ 0.89105815,  0.45264191, -0.03362558],
////           [ 0.61582931,  0.78456788,  0.07216299],
////           [-0.24815138,  0.14687234,  0.95752254],
////           [ 0.38792766,  0.92144428,  0.02127341],
////           [-0.18652825,  0.95448647,  0.23272899],
////           [ 0.51981   ,  0.76756563, -0.37502076],
////           [ 0.36809648,  0.19588353,  0.90891948],
////           [ 0.69090191,  0.57662708, -0.43606852],
////           [ 0.58192238,  0.40673352, -0.70422594],
////           [-0.12657237,  0.93791308,  0.32295277],
////           [ 0.63624344,  0.69087368,  0.34334799],
////           [-0.89355344,  0.00497404,  0.44892929],
////           [ 0.66816226,  0.74320319,  0.03475929],
////           [ 0.7542559 ,  0.23126058, -0.61450515],
////           [-0.46380568,  0.35449239,  0.8119233 ],
////           [-0.2846572 ,  0.95787531,  0.03801534],
////           [ 0.16131269,  0.36906478, -0.91529744],
////           [-0.31930673,  0.90488654, -0.2814668 ],
////           [ 0.31249945,  0.8990147 ,  0.30678439],
////           [ 0.78098609,  0.51468415, -0.35378093],
////           [ 0.0406188 ,  0.49799041, -0.86623072],
////           [-0.24006845,  0.92614786,  0.29089049],
////           [ 0.62132694,  0.09656808, -0.77757793],
////           [-0.35995381,  0.04034294,  0.93209748]];
////
////
////var posx_50_dome = [[-0.97645855,  0.0412291 , -0.21172828],
////            [ 0.72675707,  0.16051895, -0.66787561],
////            [ 0.3132297 ,  0.62079762,  0.71867759],
////            [ 0.8228432 ,  0.50439513,  0.26175299],
////            [ 0.07717594,  0.49162181, -0.86738219],
////            [ 0.54282454,  0.83737228, -0.06441417],
////            [-0.3175233 ,  0.92944416,  0.18791622],
////            [ 0.41729269,  0.01658042, -0.90862088],
////            [ 0.14655222,  0.98148383,  0.12333672],
////            [-0.84128761,  0.41257813,  0.34930567],
////            [-0.7982437 ,  0.60213293,  0.01558593],
////            [ 0.34382848,  0.77241577,  0.53399986],
////            [ 0.94441   ,  0.32340137, -0.05917187],
////            [ 0.12845778,  0.93398926,  0.33341066],
////            [-0.73976459,  0.4915651 ,  0.45946937],
////            [ 0.20834161,  0.77151993,  0.60112459],
////            [ 0.24509574,  0.96656045,  0.07542525],
////            [-0.96357067,  0.2673801 ,  0.00628085],
////            [ 0.61473062,  0.33138974,  0.71574234],
////            [ 0.88006371,  0.27358298,  0.38812398],
////            [ 0.80811868,  0.06035793, -0.58591903],
////            [ 0.17456681,  0.5694248 , -0.80329435],
////            [-0.16219736,  0.32815289,  0.93059535],
////            [-0.18078359,  0.92375985, -0.3376167 ],
////            [ 0.28179989,  0.47758484,  0.83216677],
////            [ 0.69069434,  0.33091484, -0.64299044],
////            [ 0.63739106,  0.23917638,  0.73248023],
////            [-0.12904046,  0.57591458, -0.80726139],
////            [ 0.28045977,  0.88103153, -0.38095375],
////            [ 0.99534595,  0.09450873,  0.01882943],
////            [ 0.10242409,  0.33132889, -0.93793948],
////            [ 0.87112925,  0.44194127,  0.21406016],
////            [ 0.74678598,  0.6557585 ,  0.11086704],
////            [-0.15228332,  0.20424828, -0.96700177],
////            [-0.93136644,  0.24224249, -0.27179978],
////            [-0.73267736,  0.12368369,  0.66924303],
////            [ 0.97436151,  0.18427609, -0.12908124],
////            [ 0.51140286,  0.72328288, -0.46403555],
////            [-0.62318131,  0.69410256, -0.36037021],
////            [-0.58462918,  0.56223446, -0.58489412],
////            [-0.34721128,  0.89140891, -0.29126361],
////            [-0.58409492,  0.37650216, -0.71908222],
////            [-0.71672848,  0.60562221, -0.34571958],
////            [ 0.98750259,  0.03593395,  0.15345155],
////            [-0.72610409,  0.64957734,  0.22543763],
////            [ 0.96447143,  0.13614114,  0.2264077 ],
////            [ 0.92634222,  0.34114385, -0.15972151],
////            [-0.34538008,  0.07247427, -0.93566024],
////            [ 0.95118664,  0.30738547, -0.02753464],
////            [-0.3593567 ,  0.84362827,  0.39894124]];
//
////var posx_50_dome = [[0.14834465327229837, 0.8736325341622954, -0.46342211761922564],
//// [0.6071568460764987, 0.45746315296226775, -0.6496830211297351],
//// [0.2506614409872373, 0.46176652323356254, 0.8508469427711365],
//// [0.9168066429191887, 0.30228209532039485, 0.26094274151230734],
//// [0.11191669281815485, 0.6724033233089046, 0.7316750813522267],
//// [0.7852373367962371, 0.1762902776347347, 0.5935689201033195],
//// [0.9141745828706643, 0.014558553565649675, 0.40505910747855445],
//// [-0.008871915003122538, 0.02359729307479609, -0.9996821779364278],
//// [-0.24264019583705507, 0.5418306166665122, 0.8047020058424998],
//// [0.060274929978021474, 0.04390686728841713, -0.997215683701907],
//// [-0.9424511849236255, 0.2111367400159848, 0.25924320830347075],
//// [-0.773328759346121, 0.4620973738454519, 0.4340836866933907],
//// [-0.9740004627096772, 0.22410005731277316, -0.03320034568715198],
//// [0.9977973217698665, 0.06581138643675022, -0.008328630388848396],
//// [-0.050802535202008274, 0.15446648478064667, -0.9866910395339358],
//// [0.2960332975272717, 0.8934950683159074, 0.3376845416217358],
//// [0.4501451215093404, 0.2543723032064764, -0.8559580018568514],
//// [-0.06734867908422285, 0.42663134992693796, -0.9019145451123011],
//// [0.6163272891823665, 0.7632964238770407, -0.19369884332550014],
//// [-0.20590429210061575, 0.965897601194891, 0.15698804572482467],
//// [0.5967909324293474, 0.8023624129692244, -0.007425713724207241],
//// [-0.6233596365994578, 0.2414420689575935, 0.7437260858649967],
//// [0.49407291844177303, 0.8070851871192949, -0.323273030107743],
//// [-0.503122293310633, 0.8481399469201015, 0.16591138722889598],
//// [0.7448653275403195, 0.09822290030126399, -0.6599453808343994],
//// [-0.7334420271345514, 0.5298259434616285, 0.425848872803199],
//// [-0.26448958960372854, 0.18699095238837887, 0.9460864869112857],
//// [-0.16108331387622257, 0.7445524066997962, -0.6478378498267878],
//// [-0.21988371076637273, 0.4299191744678748, -0.8756829661267092],
//// [0.876572628002212, 0.26263487542225344, -0.40329065207271175],
//// [0.21053685621504212, 0.7523108044680851, -0.6242617124697537],
//// [0.9849518761225846, 0.07503748296624034, -0.15568936338970604],
//// [-0.4906376028940718, 0.8703889803787177, -0.04120394958805934],
//// [-0.012576077912222745, 0.47698934257111475, 0.8788190993247252],
//// [0.49403045040977434, 0.6688077220025516, -0.5555449082276545],
//// [-0.8396811724562755, 0.5427326838464688, 0.019410371126370052],
//// [-0.5891851870294036, 0.6632767762635708, -0.461437681008532],
//// [-0.5846939296900273, 0.5969686171664844, 0.5493282067234203],
//// [-0.913392302855788, 0.05978955003679764, 0.4026657556711244],
//// [0.8125331236099581, 0.45869532946081265, 0.3597061547534058],
//// [-0.37058989382644236, 0.7054951000962746, 0.6041024700610433],
//// [-0.5664994867476171, 0.30067282427709724, -0.7672510568620419],
//// [0.5837257870159487, 0.03992453125483736, -0.8109687030808851],
//// [-0.5686395883487233, 0.7495697687736849, -0.33881289866703584],
//// [-0.8264014283902337, 0.21035460751524462, -0.5223137163158642],
////[0.3021332666894169, 0.6600623205299152, 0.6877741069393679],
//// [0.011365595964170102, 0.9818974852745137, -0.1890718160910435],
//// [-0.6405865350216638, 0.6796914594273301, 0.35730716635758186],
//// [0.43737844452211366, 0.6359693919768169, -0.6358010921161226],
//// [-0.9220513549206846, 0.24115870824309438, 0.30276026213400564]];
// 
//
//        thisPointer.rootObj.scale.x = thisPointer.rootObj.scale.y = thisPointer.rootObj.scale.z = 0.5;
//        thisPointer.rootObj.updateMatrix();
//        thisPointer.rootObj.frustumCulled = false;
//        
//        thisPointer.rootObj.updateMatrix();
//        thisPointer.rootObj.updateMatrixWorld();
//        thisPointer.scene.add(thisPointer.rootObj);
//
//        var bbox = new THREE.Box3().setFromObject(thisPointer.scene);
//        bbox.getCenter(thisPointer.center);
//        thisPointer.radius = thisPointer.center.distanceTo(bbox.min)
//        //console.log(thisPointer.radius);
//        thisPointer.totalobjects = index;
//        thisPointer.exterior = index; // - (thisPointer.interior).length;
//
//
////        var p = new THREE.Vector3();
////        bbox.getSize(p);
////        var tomove = p.y/2;
////
////        for(i=0; i< 50; i++) {
////            var geo = new THREE.BoxBufferGeometry(20,20,20);
////            var material = new THREE.MeshBasicMaterial({ color: 0xff0000});
////            var mesh = new THREE.Mesh( geo, material);
////             mesh.position.set(thisPointer.center.x + posx_50_dome[i][0]*(1.2*thisPointer.radius), posx_50_dome[i][1]*(p.y*1.5)+(thisPointer.center.y - 0.8*tomove), thisPointer.center.z+posx_50_dome[i][2]*(1.2*thisPointer.radius));
////
////            mesh.updateMatrixWorld();
////            thisPointer.scene.add(mesh);
////        }
//
//
////        for(i=0; i< 25; i++) {
////            var geo = new THREE.BoxBufferGeometry(20,20,20);
////            var material = new THREE.MeshBasicMaterial({ color: 0xffff00});
////            var mesh = new THREE.Mesh( geo, material);
////            mesh.position.set(thisPointer.center.x + posxcircle[i][0]*thisPointer.radius, thisPointer.center.y+posxcircle[i][1]*thisPointer.radius, thisPointer.center.z+posxcircle[i][2]*thisPointer.radius);
////            mesh.updateMatrixWorld();
////            thisPointer.scene.add(mesh);
////        }
////        for(i=0; i< 25; i++) {
////            var geo = new THREE.BoxBufferGeometry(2,2,2);
////            var material = new THREE.MeshBasicMaterial({ color: 0x00ff00});
////            var mesh = new THREE.Mesh( geo, material);
////            mesh.position.set(thisPointer.center.x + posy[i][0]*1.2*thisPointer.radius, thisPointer.center.y+posy[i][1]*1.2*thisPointer.radius, thisPointer.center.z+posy[i][2]*1.2*thisPointer.radius);
////            mesh.updateMatrixWorld();
////            thisPointer.scene.add(mesh);
////        }
////        for(i=0; i< 25; i++) {
////            var geo = new THREE.BoxBufferGeometry(2,2,2);
////            var material = new THREE.MeshBasicMaterial({ color: 0x0000ff});
////            var mesh = new THREE.Mesh( geo, material);
////            mesh.position.set(thisPointer.center.x + posz[i][0]*1.2*thisPointer.radius, thisPointer.center.y+posz[i][1]*1.2*thisPointer.radius, thisPointer.center.z+posz[i][2]*1.2*thisPointer.radius);
////            mesh.updateMatrixWorld();
////            thisPointer.scene.add(mesh);
////        }
//        //thisPointer.scene.rotateOnWorldAxis(new THREE.Vector3(0,1,0), -0.707);
//        //thisPointer.scene.updateMatrixWorld();
//
//       
//        thisPointer.controls.reset();
//        thisPointer.isLoadingMesh = false;
//        if (completionHandler) {
//            completionHandler();
//        }
//    
//    }, manager.onProgress, manager.onError);
}


View.prototype.SetColor = function() {
    for(var i=0; i<this.objs.length; i++)
    {
        var color = this.colors[Math.floor(Math.random() * this.colors.length)];
        this.objcolor[this.objs[i].name] = color;
        //this.objs[i].material.side = THREE.DoubleSide;
    }           
}


View.prototype.resetView = function() {
    this.getBoundingBoxScene();
    this.updateCamera();
    this.controls.target = this.center;
    this.controls.update();
}

View.prototype.getCameraFocustoObject = function(objindex) {

    this.updateCamera();

    var bbox = new THREE.Box3().setFromObject(this.objs[objindex]);
    var vector = new THREE.Vector3();
     bbox.getCenter(vector);//new THREE.Vector3();
    var lookat = this.objtocamera[objindex]["lookat"];
    var position = this.objtocamera[objindex]["pos"];
    vector = new THREE.Vector3(lookat[0], lookat[1], lookat[2]);
    var pos = new THREE.Vector3(position[0], position[1], position[2]);
    var dist = (this.center).distanceTo(pos);
    if(dist > this.radius){
        var ratio = (this.radius*1.0/dist)*1.5;
        this.camera.position.set(pos.x*ratio,pos.y*ratio,pos.z*ratio);//position["x"]/(dist*0.5), position["y"]/(dist*0.5), position["z"]/(dist*0.5));
    }
    else{
        var ratio = (dist*1.0/this.radius)*1.5;
        this.camera.position.set(pos.x*ratio,pos.y*ratio,pos.z*ratio);//position["x"]/(dist*0.5), position["y"]/(dist*0.5), position["z"]/(dist*0.5));
    }
    this.camera.lookAt(vector);
    var dir = new THREE.Vector3();
    this.camera.getWorldDirection(dir);
    this.camera.updateProjectionMatrix();
    this.camera.updateMatrixWorld();

    this.recolorObjects();
//    console.log("setting red color");;
    this.objs[objindex].material.color.setHex(0xff0000);
    //this.objs[objindex].material.side = THREE.DoubleSide;

    for(var i =0; i<this.objs.length; i++){
        //if(!(this.interior.includes(this.objs[i].name))){
		this.objs[i].material.transparent = true;
                //this.objs[i].material.side = THREE.DoubleSide;
		this.objs[i].material.opacity = 0.1;//UNSELECTEDOBJTRANSPARENCY;
        //}
    }
    this.objs[objindex].material.opacity = 1.0;

}

View.prototype.removeFromSelectedObs = function(indices) {
//    console.log("remove from selected objs");

    this.setAnimating(false);
    for (var i = 0; i < indices.length; i++) {
        var label = labelManager.labelForMeshObjectAtIndex(this.current_filename, indices[i]);
        if (label) {
            var color = labelManager.colorForLabel(label);
//            console.log("removing from selected objs "+color.toString());
            this.objs[indices[i]].material.color.setHex('0x'+(color.toString()).slice(1,));//setRGB(color.r, color.g, color.b);
            //this.objs[indices[i]].material.side = THREE.DoubleSide;
        }
        else {
            // this.currentlevel[indices[i]] = -1;
            //if(!this.interior.includes(indices[i].toString()))
                this.objs[indices[i]].material.color.setHex('0x'+(this.objcolor[this.objs[indices[i]].name]).substring(1,));
                //this.objs[indices[i]].material.side = THREE.DoubleSide;
        }
        this.currentlevel[indices[i]] = -1;
    
        for (var j = 0; j < this.selectedObjs.length; j++) {
            if (this.selectedObjs[j].name == (indices[i]).toString()) {
                this.selectedObjs.splice(j, 1);
                j--;
            }
        }
    }
//    for (var j = 0; j < this.selectedObjs.length; j++) {
////        console.log(this.selectedObjs[j].name);
//    }
    
};

View.prototype.deleteLabelFromSelectedObs = function(indices) {

    this.setAnimating(false);
    for (var i = 0; i < indices.length; i++) {
            this.currentlevel[indices[i]] = -1;
            //if(!this.interior.includes(indices[i].toString()))
                this.objs[indices[i]].material.color.setHex('0x'+(this.objcolor[this.objs[indices[i]].name]).substring(1,));
            //this.objs[indices[i]].material.color.setHex('0x'+("000000" + Math.random().toString(16).slice(2,8).toUpperCase()).slice(-6));
        
        for (var j = 0; j < this.selectedObjs.length; j++) {
            if (this.selectedObjs[j].name == (indices[i]).toString()) {
                this.selectedObjs.splice(j, 1);
                j--;
            }
        }
    }
};


View.prototype.unlabelledAddToSelectedObs = function(indices) {
    this.setAnimating(false);
//    console.log(indices);

    for (var i = 0; i < indices.length; i++) {
        //if(!(this.interior.includes(indices[i].toString()))){
            if(this.objs[indices[i]]){
                this.objs[indices[i]].material.color.setHex(0xffffff);
                this.selectedObjs.push(this.objs[indices[i]]);
                this.currentlevel[indices[i]] = 0;
//		    if(this.level[this.objs[indices[i]].id] === undefined) {
//			this.level[this.objs[indices[i]].id] = {};
//			this.level[this.objs[indices[i]].id][0] = [this.objs[indices[i]].id];
//			this.parentlevel[this.objs[indices[i]].id] = {};
//			this.parentlevel[this.objs[indices[i]].id][0] = this.objs[indices[i]].parent;
//		    }
           
            }
       // }
    }
};

View.prototype.addToSelectedObs = function(indices) {
    this.setAnimating(false);
//    console.log(indices);
    var selectedindices = this.indicesOfSelectedObjs();

//    console.log(selectedindices);
//    console.log(indices);
    
    for (var i = 0; i < indices.length; i++) {
        if(!(selectedindices.includes(indices[i]))) { // && !(this.interior.includes(indices[i].toString()))){
        //if(!(this.interior.includes(indices[i].toString()))){
            this.objs[indices[i]].material.color.setHex(0xffffff);
            this.selectedObjs.push(this.objs[indices[i]]);
            this.currentlevel[indices[i]] = 0;
//            if(this.level[this.objs[indices[i]].id] === undefined) {
//                this.level[this.objs[indices[i]].id] = {};
//		this.level[this.objs[indices[i]].id][0] = [this.objs[indices[i]].id];
//		this.parentlevel[this.objs[indices[i]].id] = {};
//		this.parentlevel[this.objs[indices[i]].id][0] = this.objs[indices[i]].parent;
//            }
        }
    }
};

View.prototype.toScreenPosition = function(obj)
{
    obj.updateMatrixWorld();
    var vector = new THREE.Vector3(obj.getWorldPosition.x, obj.getWorldPosition.y, obj.getWorldPosition.z);
    var vecpos2d = [];
    
    var widthHalf = 0.5*this.renderer.context.canvas.width;
    var heightHalf = 0.5*this.renderer.context.canvas.height;
   
    this.camera.updateProjectionMatrix();
    this.camera.updateWorldMatrix();
    vector.project(this.camera);

    vector.x = ( vector.x * widthHalf ) + widthHalf;
    vector.y = - ( vector.y * heightHalf ) + heightHalf;
    
    vecpos2d.push(vector);

    return vecpos2d;
};

View.prototype.toScreenPositionByVector = function(vector)
{

    
    var widthHalf = 0.5*this.renderer.context.canvas.width;
    var heightHalf = 0.5*this.renderer.context.canvas.height;

    this.camera.updateWorldMatrix();
    this.camera.updateProjectionMatrix();

    vector.project(this.camera);

    vector.x = ( vector.x * widthHalf ) + widthHalf;
    vector.y = - ( vector.y * heightHalf ) + heightHalf;

    return { 
        "x": vector.x,
        "y": vector.y,
        "z": 0
    };
};

View.prototype.colorPreviouslyLabelledObjects = function(obj_label) {
    for(var index in obj_label){
        var label = obj_label[index];
        var color = labelManager.colorForLabel(label)
        var hexcolor = (color.toString()).slice(1,);
        this.objs[index].material.color.setHex('0x'+hexcolor);
    }
}

View.prototype.recolorObjectsAtIndices = function(indices) {
	for (var j = 0; j < indices.length; j ++) {
            //if(!this.interior.includes(indices[j].toString()))
            //{
		    var label = labelManager.labelForMeshObjectAtIndex(this.current_filename,parseInt(this.objs[indices[j]].name));
		    if (label) {
			this.colorObjectAtIndices(labelManager.colorForLabel(label),[parseInt(this.objs[indices[j]].name)],false);
		    }
		    else{
			this.objs[indices[j]].material.color.setHex('0x'+(this.objcolor[this.objs[indices[j]].name]).substring(1,));
                    }
            // }
	}
}
View.prototype.recolorObjects = function() {
	for (var j = 0; j < this.objs.length; j ++) {
            //if(!this.interior.includes(this.objs[j].name))
            //{
		    var label = labelManager.labelForMeshObjectAtIndex(this.current_filename,parseInt(this.objs[j].name));
		    if (label) {
			this.colorObjectAtIndices(labelManager.colorForLabel(label),[parseInt(this.objs[j].name)],false);
		    }
		    else{
			this.objs[j].material.color.setHex('0x'+(this.objcolor[this.objs[j].name]).substring(1,));
                    }
             //}
	}
}

View.prototype.showObjectAtIndices = function(indices, shouldMoveCamera) {
    this.setAnimating(false);
//    console.log(this.selectedObjs.length);
    this.recolorObjectsAtIndices(this.indicesOfSelectedObjs());
//    for (var i = 0; i < this.selectedObjs.length; i++) {
//        this.selectedObjs[i].material.color.setHex('0x'+(this.objcolor[this.selectedObjs[i].name]).substring(1,));
//        var unselectedIndices = this.selectedObjs.map(function (obj) {
//            return parseInt(obj.name);
//        });
////        console.log("unselected indices");
//        for (var j = 0; j < unselectedIndices.length; j ++) {
////            //console.log(unselectedIndices[j])
//            this.currentlevel[unselectedIndices[i]] = -1;
//            var label = labelManager.labelForMeshObjectAtIndex(this.current_filename,unselectedIndices[j]);
////            //console.log(label)
//            if (label) {
//                this.colorObjectAtIndices(labelManager.colorForLabel(label),[unselectedIndices[j]])
//            }
//        }
//    }

    this.selectedObjs = [];

//    console.log("show object at indices");
    for (i = 0; i < indices.length; i++) {
//        console.log(indices[i]);
        this.objs[indices[i]].material.color.setHex(0xffffff);
        this.selectedObjs.push(this.objs[indices[i]]);
        this.currentlevel[indices[i]] = 0;
//        if(this.level[this.objs[indices[i]].id] === undefined) {
//	 this.level[this.objs[indices[i]].id] = {};
//	 this.level[this.objs[indices[i]].id][0] = [this.objs[indices[i]].id];
//	 this.parentlevel[this.objs[indices[i]].id] = {};
//	 this.parentlevel[this.objs[indices[i]].id][0] = this.objs[indices[i]].parent;
//        }
    }

};


View.prototype.getAllChildrenOfThisParent = function(parent, parentids, childids, childrenarray) {

    if((parent.children).length > 0)
    {
        var childrens = parent.children;

        for(c = 0; c < childrens.length; ++c)
        {
            if((childrens[c].children).length > 0)// !== undefined)
            {
                if(!(parentids.includes((childrens[c].id))))
                {
                    parentids.push(childrens[c].id);
                    this.getAllChildrenOfThisParent(childrens[c], parentids, childids, childrenarray);
                }
            }
            else
            {
                if(!(childrenarray.includes(childrens[c].id)))
                {
                    childrenarray.push(childrens[c].id);
                    childids.push(childrens[c].id);
                }
            }
        }
    }
}


View.prototype.selectParent = function() {
    for(i=0; i < this.selectedObjs.length; i++) {
        objid = this.selectedObjs[i].name;
        currlevel = this.currentlevel[objid];
        if(currlevel < 0) {
            this.currentlevel[objid] = 0;
            currlevel = 0;
        }

        if(currlevel >= 0) {
            if(Object.keys(this.hierarchy[objid]).length - 2 <= currlevel){
                continue;
            }
            var nextlevel = currlevel + 1
            this.currentlevel[objid] += 1;
            if(this.hierarchy[objid][nextlevel] === undefined)
            {
                this.currentlevel[objid] -= 1;
                continue;
            }

            var cchildren = this.hierarchy[objid][nextlevel]
            for(var k=0; k < cchildren.length; k++) {
                var id = cchildren[k];
	        //var id = this.childIdtoObjId[cchildren[k]];
	        if(id !== undefined) // && !(this.interior.includes(id.toString())))
	        {
		    this.objs[id].material.color.setHex(0xffffff);
	        }
            }            
        }
    }
}


View.prototype.selectChildren = function()
{
    var selectedObjs = this.selectedObjs;
    var newunselectedobjs = [];
    this.recolorObjects();
    for(i = 0; i < selectedObjs.length; ++i)
    {
        var objid = selectedObjs[i].name;
        var currlevel = this.currentlevel[objid];
        this.objs[objid].material.color.setHex(0xffffff);
	for(var j=0; j<currlevel; j++)
	{
	    var childrens = this.hierarchy[objid][j]; // this.level[this.objIdtoChildId[selectedObjs[i].name]][j];
	    for(c=0; c<childrens.length; ++c)
	    {
		var c_objid = childrens[c];// this.childIdtoObjId[childrens[c]];
		if((c_objid !== undefined)){ // && (!(this.interior.includes(objid.toString())))) {
		    this.objs[c_objid].material.color.setHex(0xffffff);
		}
	    } 
	}
        if(this.currentlevel[objid] > 0)
            this.currentlevel[objid] -= 1;
    }
}

//View.prototype.selectParent = function()
//{
//    var allchildren = [];
//    var anynewlevel = false;
//    for(i =0; i < this.selectedObjs.length; ++i)
//    {
////        console.log("selected component"+this.selectedObjs[i].name);
//        currlevel = this.currentlevel[this.selectedObjs[i].name];
////        console.log("current level"+ this.currentlevel[this.selectedObjs[i].name].toString());
//        if(currlevel < 0){
//          this.currentlevel[this.selectedObjs[i].name] = 0
//          currlevel = 0;
//        }
//
//        if(currlevel >= 0) {
////            console.log("current level is >= 0");
//            if(this.level[this.selectedObjs[i].id] === undefined) {
////                console.log("the levels are undefined");
////                console.log("this objects levels");
////                console.log(this.level[this.selectedObjs[i].id]);
//                this.level[this.selectedObjs[i].id] = {};
//		this.level[this.selectedObjs[i].id][0] = [this.selectedObjs[i].id];
//		this.parentlevel[this.selectedObjs[i].id] = {};
//		this.parentlevel[this.selectedObjs[i].id][0] = this.selectedObjs[i].parent;
//                currlevel = 0;
//            }
////            console.log("this objects levels");
////            console.log(this.level[this.selectedObjs[i].id])
////            console.log("this objects parentlevels");
////            console.log(this.parentlevel[this.selectedObjs[i].id])
//
//            var parentarray = [];
//            var childrenarray = [];
//
//            // Collect all the parents and childs that has been selected so far
//    
//            var isnextlevel = false;
//            if(this.level[this.selectedObjs[i].id][currlevel+1]){
//                currlevel = currlevel + 1
//                this.currentlevel[this.selectedObjs[i].name] += 1
//                isnextlevel = true;
//            }
//            for(var j=0; j<=currlevel; j++){
//               pparent = (this.parentlevel[this.selectedObjs[i].id][j]);
//               if(!this.level[this.selectedObjs[i].id][j])
//                   continue;
//
//               cchildren = (this.level[this.selectedObjs[i].id][j]).slice(0);
//               if(!(parentarray.includes(pparent.id)))
//                  parentarray.push(pparent.id);
//
//               for(var k=0; k < cchildren.length; k++){
//                   if(!(childrenarray.includes(cchildren[k]))){
//                       childrenarray.push(cchildren[k]);
//		       var id = this.childIdtoObjId[cchildren[k]];
//		       if(id !== undefined) // && !(this.interior.includes(id.toString())))
//		       {
//		           this.objs[id].material.color.setHex(0xffffff);
//                       }
//                   }
//               }
//           }
//           if(isnextlevel)
//               continue;
//
//           var parent = (this.parentlevel[this.selectedObjs[i].id][currlevel]);
//      
//           if(parent != null) {
//		   var childids = [];
//		   this.getAllChildrenOfThisParent(parent, parentarray, childids, childrenarray);
//		   if(childids.length > 0) {
//		       this.level[this.selectedObjs[i].id][currlevel+1] = childids.slice(0);
//		       this.currentlevel[this.selectedObjs[i].name] += 1;
//		       this.parentlevel[this.selectedObjs[i].id][currlevel+1] = (this.parentlevel[this.selectedObjs[i].id][currlevel]).parent;
//		       currlevel += 1;
//		       for(j = 0; j < childids.length; ++j)
//		       {
//		           var id = this.childIdtoObjId[childids[j]];
//			   if(id !== undefined) // && !(this.interior.includes(id.toString())))
//			   {
//			        this.objs[id].material.color.setHex(0xffffff);
//                           }
//                       }
//		   }
//           }
//       }
//    }
// }

//View.prototype.selectChildren = function()
//{
//    var selectedObjs = this.selectedObjs;
//    var newunselectedobjs = [];
//    this.recolorObjects();
//    for(i = 0; i < selectedObjs.length; ++i)
//    {
//        var currlevel = this.currentlevel[selectedObjs[i].name];
////        console.log(selectedObjs[i].name+"::"+currlevel.toString());
//        this.objs[selectedObjs[i].name].material.color.setHex(0xffffff);
//	for(var j=0; j<currlevel; j++)
//	{
////            console.log("hi");
//	    var childrens = this.level[this.objIdtoChildId[selectedObjs[i].name]][j];
////	    console.log(childrens);
//	    for(c=0; c<childrens.length; ++c)
//	    {
//		var objid = this.childIdtoObjId[childrens[c]];
//		if((objid !== undefined)){ // && (!(this.interior.includes(objid.toString())))) {
//		    this.objs[objid].material.color.setHex(0xffffff);
//		}
//	    } 
//	}
//        if(this.currentlevel[selectedObjs[i].name] > 0)
//            this.currentlevel[selectedObjs[i].name] -= 1;
//    }
//}

View.prototype.selectSimilar = function(){
    var selectedObjs = this.selectedObjs;
    var allselectedObjs = [];
    var newselectedObjs = [];
    var selectedObjsids = [];
    var indices = this.indicesOfSelectedObjs();

    for(var i=0; i < this.selectedObjs.length; i++) {
        selectedObjsids.push(this.selectedObjs[i].name);
    }
    for(var i=0; i < indices.length ; i++) {
        if(selectedObjsids.includes(indices[i]))
            continue;
        newselectedObjs.push(indices[i]);
    }

    for(var i=0; i < indices.length; i ++) {
        var simobjs = this.similarObjectsData[indices[i]];
        for(var j=0; j<simobjs.length; j++) {
            if(!(indices.includes(simobjs[j])))
                newselectedObjs.push(simobjs[j])
        }
    }
    
//    for (var i = 0; i < this.selectedObjs.length; i++) {
//        var objid = this.selectedObjs[i].name;
//        var simobjs = this.similarObjectsData[objid];
//        for(var j=0; j < simobjs.length; j++) {
//            if(!((this.selectedObjs).includes(simobjs[j])))
//                newselectedObjs.push(simobjs[j])
//        }
//    }
    this.addToSelectedObs(newselectedObjs);

//    for(i = 0; i < selectedObjs.length; ++i)
//    {
//        var objid = selectedObjs[i].name;
//        if(!allselectedObjs.includes(objid))
//            allselectedObjs.push(objid);
//        simobjs = this.similar[objid];
//
//        var currlevel = this.currentlevel[objid];
//	for(var j=0; j<=currlevel; j++)
//        {
//            var childrens = this.hierarchy[objid][j]; // this.level[this.objIdtoChildId[selectedObjs[i].name]][j];
//            for(c=0; c<childrens.length; ++c)
//            {
//                var c_objid = childrens[c];// this.childIdtoObjId[childrens[c]];
//                //if((objid !== undefined) && (!(this.interior.includes(objid.toString()))) && !(allselectedObjs.includes(objid)) && !(selectedObjsids.includes(objid))) {
//                if((objid !== undefined) && !(allselectedObjs.includes(objid)) && !(selectedObjsids.includes(objid))) {
//                    newselectedObjs.push(objid); 
//                    allselectedObjs.push(objid);
//                }
//            } 
//        }
//    }
//  
// //   var x =  allselectedObjs.slice(0);//selectedObjids.slice(0);
//    var similarObjids = [];
//    for(var i=0 ;i< allselectedObjs.length; i++)
//        similarObjids.push(parseInt(allselectedObjs[i]));
////    console.log(similarObjids);
//    for(var i=0 ;i< allselectedObjs.length; i++){
//        var selectedObjid = allselectedObjs[i];
//        
//        // if(!(this.interior.includes(selectedObjid.toString()))) {
//            var currentFileSimilarData = this.similarObjectsData;
//
//            if (currentFileSimilarData != null) {
//                var similarindices = currentFileSimilarData[selectedObjid.toString()];
//                for(var k=0; k<similarindices.length; k++){
//                    this.objs[similarindices[k]].material.color.setHex(0xffffff);
//                    if(!(similarObjids.includes(parseInt(similarindices[k]))) && !(allselectedObjs.includes(similarindices[k]))){
//                        similarObjids.push(parseInt(similarindices[k]));
//                    }
//                }
//            }
//       // }
//    }
//    this.addToSelectedObs(similarObjids);
}

//View.prototype.selectSimilar = function(){
//    var selectedObjids =  this.indicesOfSelectedObjs();
//    var childrenarray = [];
//    for(i =0; i < this.selectedObjs.length; ++i)
//    {
//        if(!(childrenarray.includes(this.selectedObjs[i].id))){
//	    childrenarray.push(this.selectedObjs[i].id);
//	}
//        currlevel = this.currentlevel[this.selectedObjs[i].name];
//        for(var j=0; j<currlevel; j++){
//           cchildren = (this.level[this.selectedObjs[i].id][j]).slice(0);
//
//           for(var k=0; k < cchildren.length; k++){
//	     if(!(childrenarray.includes(cchildren[k]))){
//	       childrenarray.push(cchildren[k]);
//	     }
//          }
//       }
//    }
//    var similarObjids = [];// selectedObjids.slice(0);
//    for(var i=0 ;i< childrenarray.length; i++){
//        var selectedObjid = this.childIdtoObjId[childrenarray[i]];
//        
//        if(!(this.interior.includes(selectedObjid.toString()))) {
//            var currentFileSimilarData = this.similarObjectsData;
//
//            if (currentFileSimilarData != null) {
//                var similarindices = currentFileSimilarData[selectedObjid.toString()];
//                for(var k=0; k<similarindices.length; k++){
//                    this.objs[similarindices[k]].material.color.setHex(0xffffff);
//                    if(!(similarObjids.includes(parseInt(similarindices[k]))) && !(childrenarray.includes(this.objIdtoChildId[similarindices[k]]))){
//                        similarObjids.push(parseInt(similarindices[k]));
//                    }
//                }
//            }
//        }
//    }
//    this.addToSelectedObs(similarObjids);
//    //this.showObjectAtIndices(similarObjids);
//}

View.prototype.moveCameraToPosition = function(cameraPosition, cameraDirection, animated) {
    if (animated) {

        var thisPointer = this;
        var currentCameraPosition = this.camera.position.clone();
        this.controls.reset();

        var tweenUpdate = function() {
            var sinPhi = Math.sin(current.z);
            var x = current.x * Math.cos(current.y) * sinPhi;
            var y = current.x * Math.sin(current.y) * sinPhi;
            var z = current.x * Math.cos(current.z);
            thisPointer.camera.position.set(x, y, z);
            thisPointer.camera.lookAt(thisPointer.scene.position)
        };

        var r = Math.sqrt(currentCameraPosition.x * currentCameraPosition.x+
            currentCameraPosition.y * currentCameraPosition.y+
            currentCameraPosition.z * currentCameraPosition.z);
        var theta = Math.atan2(currentCameraPosition.y , currentCameraPosition.x);
        var phi = Math.acos(currentCameraPosition.z / r);

        var toR = Math.sqrt(cameraPosition.x * cameraPosition.x+
            cameraPosition.y * cameraPosition.y+
            cameraPosition.z * cameraPosition.z);
        var totTheta = Math.atan2(cameraPosition.y , cameraPosition.x);
        var toPhi = Math.acos(cameraPosition.z / toR);

        var current = new THREE.Vector3(r, theta, phi);
        var target = new THREE.Vector3(toR, totTheta, toPhi);

        //var lookAtTarget = new THREE.Vector3();
        //lookAtTarget.addVectors(cameraDirection, cameraPosition);

        TWEEN.removeAll();


        //this.controls.target = lookAtTarget;
        //this.camera.position.set(
        //    cameraPosition.x - lookAtTarget.x,
        //    cameraPosition.y - lookAtTarget.y,
        //    cameraPosition.z - lookAtTarget.z);
        //this.camera.lookAt(lookAtTarget);


        var positionTween = new TWEEN.Tween(current)
            .to(target, 2000)
            .easing(TWEEN.Easing.Sinusoidal.Out)
            .onUpdate(tweenUpdate)
        positionTween.start();

        new TWEEN.Tween(this.camera.rotation)
            .to(THREE.Euler(), 2000)
            .easing(TWEEN.Easing.Sinusoidal.Out)
            .start();

    }
    else {
        this.camera.position.set(cameraPosition.x, cameraPosition.y, cameraPosition.z);
    }
};

View.prototype.setCameraConfig = function(cameraConfig) {
    this.camera.position.set(cameraConfig.position.x,cameraConfig.position.y,cameraConfig.position.z);
    //TODO: set lookAt and rotation too.
};

View.prototype.setAnimating = function (isAnimating) {
    if (isAnimating == this.isAnimating) return;
    this.controls.reset();
    this.rootObj.rotation.x = this.rootObj.rotation.y = this.rootObj.rotation.z = 0.0;
    //this.scene.rotation.x = this.scene.rotation.y = this.scene.rotation.z = 0.0;
    // for(var i=0; i < this.objs[i].length; i++)
    //     this.objs[i].rotation.x = this.objs[i].rotation.y = this.objs[i].rotation.z = 0.0;  
    this.isAnimating = isAnimating;
    //this.controls.enabled = !isAnimating;
};

//View.prototype.indicesOfSelectedObjs = function () {
//    var indices = [];
//    for (var i = 0; i < this.selectedObjs.length; i++) {
////        console.log(this.selectedObjs[i].name);
//        objid = this.selectedObjs[i].name;
//        var currlevel = this.currentlevel[this.selectedObjs[i].name];
//        for(var j=0; j<=currlevel; j++)
//	{
//	    var childrens = this.level[this.objIdtoChildId[this.selectedObjs[i].name]][j];
//	    for(c=0; c<childrens.length; ++c)
//	    {
//		var objid = this.childIdtoObjId[childrens[c]];
//		// if((objid !== undefined) && (!(this.interior.includes(objid.toString())))&& !(indices.includes(objid))) {
//		if((objid !== undefined)&& !(indices.includes(objid))) {
//                    indices.push(objid);
//		}
//	    } 
//	}
//        //indices.push(this.objs.lastIndexOf(this.selectedObjs[i]));
//    }
//    return indices;
//};

View.prototype.indicesOfSelectedObjs = function () {
    var indices = [];
    for (var i = 0; i < this.selectedObjs.length; i++) {
        objid = this.selectedObjs[i].name;
        var currlevel = this.currentlevel[objid];
        for(var j=0; j<=currlevel; j++)
	{
            var childrens = this.hierarchy[objid][j];
            if(childrens === undefined){
                continue;
            }
	    for(c=0; c<childrens.length; ++c)
	    {
		//var c_objid = this.childidtoobjid[childrens[c]];
		var c_objid = childrens[c];
		if((c_objid !== undefined)&& !(indices.includes(c_objid))) {
                    indices.push(c_objid);
		}
	    } 
	}
    }
    return indices;
};

View.prototype.objnameOfSelectedObjs = function () {
    var objnames = [];
    for (var i = 0; i < this.selectedObjs.length; i++) {
        objnames.push(this.objnames[this.objs.lastIndexOf(this.selectedObjs[i])]);
    }
    return objnames;
};


View.prototype.currentCameraSetUp = function () {
    //TODO: see how to get lookAt and rotation vector
    return new CameraSetUp(this.camera.position, new THREE.Vector3(), new THREE.Vector3());
};

//********* Event Handling  **********//

View.prototype.onWindowResize = function() {
    
    this.renderer.setSize(this.frame.width, this.frame.height);
    this.camera.aspect = this.frame.width / this.frame.height;
    this.camera.updateProjectionMatrix();
     //converting window co-ordinate system to raycaster coordinate system(-1 -- 0 -- +1).
};

View.prototype.checkObjectsIntersects = function() {
    
    // get all camera positions - 
    // theta = 2* np.pi * np.random.uniform(0.0,1.0,numpoints);
    //// HEMISPHERE
    // phi = np.arccos(1 - np.random.uniform(0.0, 1.0, numpoints));
    //// SPHERE
    // phi = np.arccos(1 - 2*np.random.uniform(0.0,1.0, numpoints));

    // x = np.sin(phi) * np.cos(theta)
    // y = np.sin(phi) * np.sin(theta)
    // z = np.cos(phi)

    var vector = new THREE.Vector3();
    for(var i=0; i < this.objs.length; i++){
        var bbox = new THREE.Box3().setFromObject(this.objs[i]);
        //this.objs[i].getWorldPosition(vector);
        bbox.getCenter(vector);
        //vector.sub(this.camera.position);
        this.camera.lookAt(vector);
        var dir = new THREE.Vector3();
        this.camera.getWorldDirection(dir);
        this.camera.updateProjectionMatrix();
        this.camera.updateMatrixWorld();
        var raycaster = new THREE.Raycaster(this.camera.position, dir.normalize());
        var intersects = raycaster.intersectObjects(this.objs);

        if(intersects.length > 0){
            var selectedObjidx = this.objs.lastIndexOf(intersects[0].object);
            
            if(!this.visibleindices.includes(selectedObjidx)) {
//                //console.log(selectedObjidx);
                this.visibleindices.push(selectedObjidx);
                // this.objs[i].material = new THREE.MeshPhongMaterial({
                // //color: this.objcolor[this.objs[i].name],
                // color: '#ff0000',
                // specular: 0x141414,
                // shininess: 20,
                // flatShading: true
                // });
            }
        }
    }

};

View.prototype.checkObjectsIntersectsByRenderer = function(obj) {
//    //console.log("******"+obj.name+"*****");
    this.render();
    var canvas = (document.getElementById("container-color")).children[0];
    var gl = canvas.getContext("webgl", {preserveDrawingBuffer: true});
    var pixels = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
    gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight, gl.RGBA, gl.UNSIGNED_BYTE, pixels);

    var redpixel = 0;

    
    var pos2d = this.toScreenPosition(obj);
    var width = Math.round(Math.abs(pos2d[1].x - pos2d[2].x));
    var height = Math.round(Math.abs(pos2d[1].y - pos2d[2].y));
    var xstart = Math.round(Math.min(pos2d[1].x, pos2d[2].x));
    var ystart = Math.round(Math.min(pos2d[1].y , pos2d[2].y));
    var count = 0;
    for(var i = xstart; i< xstart + width; i++)
    {
        if(redpixel > 100)
            break;

        if(count > 5000)
            break

        for(var j =ystart; j < ystart +height; j++){
            redComponent = pixels[((i * (gl.drawingBufferWidth * 4)) + (j * 4)) + 0];
            
            count += 1;
            if(redComponent > 200) {
//                //console.log(i.toString()+"::"+j.toString()+"::"+(((i * (gl.drawingBufferWidth * 4)) + (j * 4)) + 0).toString());
                redpixel += 1;
                if(redpixel > 100)
                    break
            }
        }
    }

//    //console.log(redpixel);
    if(redpixel > 100)
        return true
    return false;

};

View.prototype.removeTransparency = function() {

    for(var i =0; i<this.objs.length; i++){
        //if(!(this.interior.includes(this.objs[i].name))){
		if((this.objs[i].material.color).getHexString() == "ff0000"){
		    this.objs[i].material.color.setHex('0x'+(this.objcolor[this.objs[i].name]).substring(1,));
		}
		this.objs[i].material.opacity = 1.0;
		this.objs[i].material.transparent = false;
        //}
    }
}

View.prototype.onMouseDown = function(event) {
    if (this.isAnimating || event.button != 2) return;
    event.preventDefault();
    this.camera.updateMatrixWorld();

    this.raycaster.setFromCamera(this.mouse, this.camera);

    var intersects = this.raycaster.intersectObjects(this.objs);
    if (intersects.length > 0 ) {
        this.removeTransparency();
        if (event.altKey && event.ctrlKey) {
//            console.log("alt and control key");
            var selectedObjidx = this.objs.lastIndexOf(intersects[0].object);
            // if(!(this.interior.includes(selectedObjidx.toString()))) {

                var currentFileSimilarData = this.similarObjectsData;
                if (currentFileSimilarData != null) {
                    for (var i = 0; i < currentFileSimilarData.length; i++) {
                        var dataArray = currentFileSimilarData[i];
                        for (var j = 0; j < dataArray.length; j++) {
                            if (selectedObjidx == dataArray[j]) {
                                if (this.selectedObjs.filter(function(obj) {return obj.id == intersects[0].object.id})[0]) {
                                    this.removeFromSelectedObs(dataArray);
                                }
                                else {
                                    this.addToSelectedObs(dataArray);
                                }
                                break;
                            }
                        }
                    }
                }
           // }
        }
        else if(event.ctrlKey || event.metaKey) {      //this.keysPressed.indexOf(65) != -1 for reverting to A key
            if (this.selectedObjs.filter(function(obj) {return obj.id == intersects[0].object.id})[0]) {
                var selectedObjidx = this.objs.lastIndexOf(intersects[0].object)
                //if(!(this.interior.includes(selectedObjidx.toString())))
                    this.removeFromSelectedObs([selectedObjidx]);
            }
            else {
                var selectedObjidx = this.objs.lastIndexOf(intersects[0].object)
               // if(!(this.interior.includes(selectedObjidx.toString())))
                    this.addToSelectedObs([selectedObjidx]);
            }
        }
        else {
//            console.log("only right click");
//            console.log(this.objs.lastIndexOf(intersects[0].object));
            var selectedObjidx = this.objs.lastIndexOf(intersects[0].object);
           
            //if(!(this.interior.includes(selectedObjidx.toString()))){
//            //    console.log(selectedObjidx);
                this.showObjectAtIndices([selectedObjidx], true);
            //} else {
//                var count = 1;
//                var selectedObjidx = -1;
//                while(count < intersects.length){
//                    selectedObjidx = this.objs.lastIndexOf(intersects[count].object);
//                    if(!(this.interior.includes(selectedObjidx.toString()))){
////                         console.log(selectedObjidx);
//                         break;
//                    }
//                    count++;
//                }
//                if(selectedObjidx != -1)
//                    this.showObjectAtIndices([selectedObjidx], true);
//                else {
////                    console.log("nothing clicked");
//                    if(event.which === 3 || event.button === 2){
//                        this.removeTransparency();
//	            }
////                    console.log("in else showing object indices");
//                    this.recolorObjects();
//                    this.showObjectAtIndices([]);
//                }
//            }
        }
    }
    else {
//        console.log("nothing clicked");
        if(event.which === 3 || event.button === 2){
            this.removeTransparency();
	}
//        console.log("in else showing object indices");
        this.recolorObjects();
        this.showObjectAtIndices([]);
    }
};

View.prototype.onMouseMove = function(event) {
    event.preventDefault();

    //converting window co-ordinate system to raycaster coordinate system(-1 -- 0 -- +1).
    
    this.mouse.x = (((event.clientX +window.scrollX) - this.frame.left) / this.frame.width*1.0) * 2.0 - 1;
    this.mouse.y = - (((event.clientY+window.scrollY) -this.frame.top)/ this.frame.height*1.0) * 2.0 + 1;
};

View.prototype.onMouseUp = function(event) {
    if (this.isAnimating) return;
    event.preventDefault();
};


View.prototype.onKeyDown = function(event) {
    if (event.which == 8 || event.which == 46)
    {
        var selectedObjidxs =  this.indicesOfSelectedObjs();
        this.deleteLabelFromSelectedObs(Array.from(selectedObjidxs));
    }
    else if(event.which == 13){
        this.selectedObjidxs = this.indicesOfSelectedObjs();
    }
    else if (event.which != 91 || event.which != 92) { //Not recording window switching things. (91 & 92 windows keys)
        this.keysPressed.push(event.which);
    }
//    else if (event.keyCode == 187) {
//        this.camera.position.set(this.camera.position.x+10, this.camera.position.y, this.camera.position.z);
//    }
//    else if (event.keyCode == 189) {
//        this.camera.position.set(this.camera.position.x-10, this.camera.position.y, this.camera.position.z);
//    }

};

View.prototype.onKeyUp = function(event) {
    this.keysPressed = this.keysPressed.filter(function (key) {
        return key != event.which;
    });
};

function download(content, fileName, contentType){
    return new Promise(function(resolve,reject){
       
        var a = document.createElement("a");
        var file = new Blob([content], {type: contentType});
        url = URL.createObjectURL(file);
        a.href = url;
        a.download = fileName;
        a.click();
        setTimeout(() => {
          URL.revokeObjectURL(url);
          a.remove()
          resolve("suceess");
        }, 500);
    });
};

async function getJsonMetaDataFiles(filename, geoid) {

    var prevPromise=Promise.resolve();
    prevPromise=prevPromise.then(function(){
        return download(JSON.stringify(geoid), filename, 'application/json');
    }).then(function(data){
//        console.log(data);
    }).
    catch(function(error){
//        console.log(error);
    });
};
