
function getJsonData(callback) {

    $.getJSON("js/nonavailfiles.json", function( data0 ) {
        $.getJSON("js/allfacesdata.json", function( data1 ) {
           $.getJSON("js/allcomponents.json", function(data2){
               result = {"nonavail":data0, "numfacesdata":data1["faces"],"allcompdata":data2["totalcomps"]};
               callback(result);
            });
        });
    });

}

function loadJsonFromPHP( filenames, folder) {

    var objs = [];
    var objnames = [];
   
    var filename = [];

    for (var i = 0; i < filenames.length; i++) { 
        console.log(filenames[i]);
        filename.push(filenames[i].slice(0, -1));
    }

//    this.getfacefiles(filename);

    var index = 0;
    var totalcomps = {};
    var numfacesdata = {};
    var allcompdata = {};
    var nonavail = [];
    getJsonData(function(data) {
        nonavail = data["nonavail"];
        numfacesdata = data["numfacesdata"];
        allcompdata = data["allcompdata"];
        for(var i = 0; i < filenames.length; i++) {
            filename = filenames[i].slice(0, -1);
            if(nonavail.includes(filename)){
                continue;
            }
            console.log(numfacesdata[filename]);
            
            if(numfacesdata[filename] && allcompdata[filename] && numfacesdata[filename] <= 100000 && allcompdata[filename] <= 20000)
            {
                    this.ComputerFeatureCollLoader(filename);
                    //this.checkIfComponentIsInternal(filename,folder);
            }
            //this.ComputerFeatureCollLoader(filename);
            //this.checkIfComponentIsInternal(filename, folder);
        }
    });

}

function getfiles(filename) {
    totalcomps = {};
    var prevPromise=Promise.resolve();
    filename.forEach(function(fname){
        prevPromise=prevPromise.then(function(){
            return getInternalExternal(fname, totalcomps);
        }).then(function(data){
            totalcomps = data;
            console.log(data);
        }).
        catch(function(error){
            console.log(error);
        });
    }); 

    prevPromise.then(function() {
        console.log(totalcomps);
        result['totalcomps'] = totalcomps;
        getJsonMetaDataFiles("allcomponents.json", result);
    });

    return totalcomps
}

async function getInternalExternal(filename, totalcomps) {
    return new Promise(function(resolve,reject){
        
        var colladaloader = new THREE.ColladaLoader();
        colladaloader.load('files/batch_dae/'+filename+".dae", function(collada) {
            
            var rootObj = collada.scene;
            var index = 0;
           
            rootObj.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                    index++;
                }
            });
            totalcomps[filename] = index;
            console.log(totalcomps[filename]);
        });

        //resolve(totalcomps);
        setTimeout(() => {
          resolve(totalcomps);
        }, 500);
    });
}

function getfacefiles(filename) {
    allfacesdata = {};
    var prevPromise=Promise.resolve();
    filename.forEach(function(fname){
        prevPromise=prevPromise.then(function(){
            return getNumfaces(fname, allfacesdata);
        }).then(function(data){
            allfacesdata = data;
            console.log(data);
        }).
        catch(function(error){
            console.log(error);
        });
    }); 

    prevPromise.then(function() {
        console.log(allfacesdata);
        result  = {}
        result['faces'] = allfacesdata;
        getJsonMetaDataFiles("allfacesdata.json", result);
    });

    return allfacesdata;
}
async function getNumfaces(filename,  allfacesdata) {
    console.log(filename)
    return new Promise(function(resolve, reject){

    var colladaloader = new THREE.ColladaLoader();
        colladaloader.load('files/meshes/'+filename+".dae", function(collada) {
       
            var rootObj = collada.scene;
            var numfaces = 0; 
            rootObj.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                        if(child && child.geometry && child.geometry.faces)
			    numfaces += (child.geometry.faces).length
//                        if(child.geometry !== undefined && child.geometry !== null){
//			    var geometry = new THREE.Geometry().fromBufferGeometry( child.geometry );
//			    numfaces += geometry.faces.length;
//                        }
                    }
            });
            allfacesdata[filename] = numfaces;
            console.log(allfacesdata);
        });
        setTimeout(() => {
            resolve(allfacesdata);
        },500);
       });
}

async function getJsonFiles(filename, level) {

    console.log("level length");
    console.log(Object.keys(level).length);

    var index = 0;
    var prevPromise=Promise.resolve();

    var indexes = [];
    for (var k in level){
        if (level.hasOwnProperty(k)) {
             
            indexes.push(k);
            index++;
        }
    }

           
    //    var titles=document.getElementById('titles').value;
    // titles=titles.split(',');
    var prevPromise=Promise.resolve();
    indexes.forEach(function(index){
        prevPromise=prevPromise.then(function(){
            var fullfilename = filename+"_"+index.toString()+".json";
            console.log(fullfilename);
            return download(JSON.stringify(level[index]), fullfilename, 'application/json');
        }).then(function(data){
            console.log(data);
        }).
        catch(function(error){
            console.log(error);
        });
    }); 
}
function URLExists(url){
    var http = new XMLHttpRequest();
    http.open('HEAD',url,false);
    http.send();
    if(http.status == 404)
        return false;
    else
        return true;
}

function download(content, fileName, contentType){
    let resolved =  new Promise(function(resolve,reject){
  
        var a = document.createElement("a");
        var file = new Blob([content], {type: contentType});
        url = URL.createObjectURL(file);
        a.href = url;
        a.download = fileName;
        a.click();
        setTimeout(() => {
          URL.revokeObjectURL(url);
          a.remove();
          resolve("suceess");
        }, 500);
    });
     let timeout =  new Promise(function(resolve,reject){
         setTimeout(() => {
           reject("failure");
         }, 500);
     });

     let race = Promise.race([
         resolved,
         timeout
     ])
   return race;
}


function ComputerFeatureCollLoader(filename) {
    
    var colladaloader = new THREE.ColladaLoader();
        colladaloader.load('files/meshes/'+filename+".dae", function(collada) {
            
            var rootObj = collada.scene;
            var index = 0;
            var geoid = {};
           
            rootObj.traverse(function(child) {
                if (child instanceof THREE.Mesh) {
                    var geometry = new THREE.Geometry().fromBufferGeometry( child.geometry );
                    // console.log((geometry.vertices).length);
                    // console.log((geometry.faces).length);
                    child.geometry.computeBoundingBox();
                    var centroid = new THREE.Vector3();
                    child.geometry.boundingBox.getCenter(centroid);
                    centroid.applyMatrix4( rootObj.matrixWorld );
                    
                    var map = "none";
                    if(child.material.map != null)
                        map = child.material.map.uuid;
                    var material = {"name": child.material.name, "color": child.material.color, "map":map}

                    var vertices = [];
                    
                    for(var i=0; i< geometry.vertices.length; i++) {
                        vertices.push(geometry.vertices[i].applyMatrix4( rootObj.matrixWorld ));
                    }
                    //child.name = index

                    //console.log(child.name+"::"+child.id+"::"+index.toString());
                
                    if(child.name.length <= 0)
                        child.name = "_None";

                    if(!(child.name in geoid))
                        geoid[child.name] = [];

                    
                    (geoid[child.name]).push({"index":index.toString(), "v": vertices, "f":geometry.faces.length, "faces":geometry.faces,"c": centroid, "m":material});
                    index++;
                    
                }
            });
            console.log(index);

            data = JSON.stringify(geoid);
            this.getJsonMetaDataFiles(filename+"_metadata.json", data);
             
        });
}

async function getJsonMetaDataFiles(filename, data) {

    //var prevPromise=Promise.resolve();
    //prevPromise=prevPromise.then(function(){
 //       console.log(sizeof(data));

       // var j = JSON.stringify(data);
       return download(JSON.stringify(data), filename, 'application/json').then(function(data){
       console.log(data);
   }).
   catch(function(error){
       console.log(error);
   });
}


function callbackFunc(response){
    console.log("ok");
}

function checkIfComponentIsInternal(filename, folder) {
     
    var colladaloader = new THREE.ColladaLoader();
    //colladaloader.load('files/'+folder+'/'+filename+".dae",function(collada){
    colladaloader.load('files/batch_dae/'+folder+"/"+filename+".dae", function(collada) {
    //colladaloader.load('js/meshes/'+filename+".dae", function(collada) {
        
        var rootObj = collada.scene;
        var index = 0;
        var objs = [];
       
        var numfaces = 0;
        var tobreak = false;
        rootObj.traverse(function(child) { 
            if(tobreak)
            {
                return true;
            }
            if (child instanceof THREE.Mesh) {
                child.name = index.toString();
                objs.push(child);
                var geometry = new THREE.Geometry().fromBufferGeometry( child.geometry );
                numfaces += geometry.faces.length;

                if(numfaces > 100000)
                {
                    tobreak = true;
                    return true;
                }
                index++;
                if(index > 20000){
                    tobreak = true;
                     return true;
                }
            }
        });
        if(tobreak){
            console.log(numfaces);
            console.log("num faces > 100000");
            return true;
        }
        if(index > 20000)
        {
            console.log("num components > 20000");
            return true;
        }
        console.log("proceeding to download files");

        rootObj.scale.x = rootObj.scale.y = rootObj.scale.z = 0.5;
        rootObj.updateMatrix();
        var bbox = new THREE.Box3().setFromObject(rootObj);
        var center = new THREE.Vector3();
        bbox.getCenter(center);
        var radius = center.distanceTo(bbox.min);

        var camera_location = [];

        var x = [];
        var y = [];
        var z = [];
        var numpoints = 50;

        if(numpoints == 10)
        {
        x = [-0.82393722, -0.24653998, -0.22198893, -0.44438536,  0.94389089,
       -0.17606492,  0.21616699,  0.66012889, -0.81872851,  0.51338206];

        y = [-0.55404214,  0.18781899,  0.64786437,  0.74529609,  0.30488132,
        0.79962054,  0.80410963, -0.69641142,  0.46606217, -0.71837552];

        z = [ 0.11901587, -0.95075868,  0.72869244,  0.49704666, -0.1269542 ,
        0.57411509,  0.55378654, -0.28149774,  0.33536501,  0.46944166];
        }
        if(numpoints == 25)
        {
        x = [-0.35739573, -0.56201231, -0.51750999, -0.03506302, -0.62106791,
       -0.46574575, -0.86766211,  0.59755903,  0.93456248, -0.3979698 ,
       -0.05320801,  0.6117628 ,  0.21482899, -0.31547917,  0.08059177,
        0.80226672, -0.77858335,  0.00407692,  0.76809425,  0.95460055,
        0.90838412,  0.43342297, -0.48901546,  0.065988  ,  0.04411432];

        y = [ 0.60134266,  0.6887466 ,  0.84845513, -0.4492627 , -0.3170525 ,
       -0.81225986,  0.28273233, -0.56548164,  0.15112686,  0.88237996,
        0.3200218 ,  0.78959272, -0.3020886 ,  0.86800397, -0.6924667 ,
       -0.02504248, -0.08936063,  0.37912066, -0.07580724,  0.03722419,
        0.35780754, -0.58734141, -0.0258959 , -0.86236944,  0.25086094];

        z = [ 0.71460149,  0.45800686,  0.11093829, -0.89271138,  0.71676521,
        0.35116209,  0.40893141,  0.56846611, -0.32210814, -0.2510491 ,
        0.94591488, -0.04784985, -0.92875776,  0.38346055,  0.71693433,
       -0.59644026,  0.62114624,  0.92533826, -0.63583369,  0.29555397,
       -0.21636094,  0.68350172, -0.87189064, -0.50196069, -0.96701743];
        }
        if(numpoints == 50)
        {
        x=[ 0.15753856,  0.29294976, -0.59851876,  0.03776113,  0.04633704,
        0.81146018,  0.45059962, -0.43797725, -0.7182811 , -0.64818318,
       -0.70015126,  0.73835798,  0.67965192,  0.10605871,  0.08807405,
        0.62628742, -0.23962841,  0.19765276,  0.03230463,  0.43781975,
        0.35232644,  0.01705111,  0.21069447,  0.0719487 , -0.58194712,
       -0.2208143 , -0.06503552, -0.55281348,  0.57841497,  0.53853598,
       -0.9484292 , -0.56300556,  0.96823431, -0.2768108 ,  0.99114744,
        0.21162183, -0.50094911, -0.04452281, -0.43211254,  0.38715222,
       -0.17242207, -0.57380644, -0.19710073,  0.72001547, -0.25225693,
        0.56031466,  0.69345741, -0.79148893, -0.4703627 ,  0.17690929];
        y =[ 0.98075944, -0.51415628,  0.12855481,  0.26530424,  0.4476264 ,
        0.11985013, -0.23095228,  0.8982496 ,  0.42883514,  0.6489153 ,
       -0.59423595, -0.62541624, -0.73142784, -0.63901325,  0.93941454,
       -0.36379824, -0.45702042,  0.26781664, -0.70837396, -0.42934141,
        0.39531137, -0.35137999, -0.52930231, -0.97331246, -0.67973924,
        0.73641224, -0.95649678, -0.52282752,  0.81326285,  0.4526233 ,
        0.17133836, -0.66968916,  0.03403068,  0.38875856, -0.12561207,
        0.94930708, -0.3946005 , -0.32660719, -0.29503705,  0.38422383,
       -0.63005513, -0.68830212,  0.97189191,  0.68218725,  0.08775053,
       -0.54619754, -0.42549158, -0.28716602, -0.48754891,  0.30762742];
       z=[ 0.11529324,  0.80611647,  0.79072686, -0.96342501,  0.89301931,
        0.5719863 , -0.86233464,  0.0363812 , -0.54788017, -0.39845639,
       -0.39581794,  0.25235295, -0.05555697,  0.76184881, -0.33127523,
       -0.68950337,  0.85656906,  0.94297807, -0.70509768,  0.78992393,
       -0.84828945, -0.93607765, -0.82185577,  0.21791338, -0.44642145,
       -0.63948264, -0.28440163,  0.64888261, -0.06355832,  0.71071172,
       -0.2666931 , -0.48429451,  0.24771804, -0.87877333, -0.04299254,
       -0.23244842, -0.77028594,  0.94411094,  0.8521924 ,  0.83814391,
       -0.75716654,  0.44383146, -0.12875336, -0.12727249, -0.96367333,
       -0.62266823, -0.58144109,  0.53951919, -0.7355644 , -0.93491629];
        }
       
        for(var i=0; i < x.length; i++) {
            var position = new THREE.Vector3(x[i]*2*radius+center.x, y[i]*2*radius+center.y, z[i]*2*radius+center.z);
            camera_location.push(position);
        }
        getInterior(filename, camera_location, objs);
        //getJsonMetaDataFiles(filename+"_cameralocation", camera_location);
    });
}


function getInterior(filename, cameraPositions, objs) {
 var camera = new THREE.PerspectiveCamera(70, 1, 0.01, 5000);
 var visibleindices = [];
 var objtocamera = {};
 for(var c=0; c< cameraPositions.length; c++) {
     var position = cameraPositions[c];
     camera.position.set(position.x, position.y, position.z);
     camera.updateProjectionMatrix();
     camera.updateMatrixWorld();
     //console.log(camera.position);
     checkObjectsIntersects(camera, objs, visibleindices,objtocamera);
     // console.log(objtocamera);
     // console.log(visibleindices);
 }


 interior = [];

 for(var i=0; i < objs.length; i++){
     if(!(visibleindices.includes(Number(objs[i].name)))) {
     //console.log(this.objs[i].name);
     interior.push(objs[i].name);
     }
 }
 //console.log(interior);

 result = {"interior":interior, "objtocamera": objtocamera};
 getJsonMetaDataFiles(filename+"_interior_objtocamera.json",result);   

    // var prevPromise=Promise.resolve();
    // prevPromise=prevPromise.then(function(){
    //     return getJsonMetaDataFiles(filename+"_interior.json",interior);
    // }).then(function(data){
    //     console.log(data);
    // }).
    // catch(function(error){
    //     console.log(error);
    // });

    // prevPromise.then(function(){
    //  return getJsonMetaDataFiles(filename+"_objtocamera.json",objtocamera);   
    // }).then(function(data){
    //     console.log(data);
    // }).
    // catch(function(error){
    //     console.log(error);
    // });
    

 
 
    //setTimeout(() => {
     
    //}, 500);
    //setTimeout(() => {
    
     
    //}, 1000);
  
}

function checkObjectsIntersects(camera, objs, visibleindices,objtocamera) {

    var vector = new THREE.Vector3();
    for(var i=0; i < objs.length; i++){
        var bbox = new THREE.Box3().setFromObject(objs[i]);
        //this.objs[i].getWorldPosition(vector);
        bbox.getCenter(vector);
        //vector.sub(this.camera.position);
        camera.lookAt(vector);
        var dir = new THREE.Vector3();
        camera.getWorldDirection(dir);
        camera.updateProjectionMatrix();
        camera.updateMatrixWorld();
        var raycaster = new THREE.Raycaster(camera.position, dir.normalize());
        var intersects = raycaster.intersectObjects(objs);

        if(intersects.length > 0){
            var selectedObjidx = objs.lastIndexOf(intersects[0].object);
            
            if(!visibleindices.includes(selectedObjidx)) {
                visibleindices.push(selectedObjidx);
                // console.log(selectedObjidx);
                // console.log(camera.position);
                // console.log(vector);
                objtocamera[selectedObjidx] = {"pos":[camera.position.x, camera.position.y, camera.position.z],"lookat":[vector.x, vector.y, vector.z]};
                // console.log(objtocamera);
            }
        }
    }

};
