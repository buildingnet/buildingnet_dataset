/**
 * Created by rajendrahn on 02/02/16
 */


function vectorFromData(data) {
//    console.log(data);
    return new THREE.Vector3(data["x"], data["y"], data["z"]);
}

function Color(r, g, b) {
    this.r = r / 255.0;
    this.g = g / 255.0;
    this.b = b / 255.0;
}

function createColorFromData(data) {
    return new Color(data["r"], data["g"], data["b"]);
}

function MeshObject(cameraSetUp, index) {
    this.cameraSetUp = cameraSetUp;
    this.index = index;
}

function createMeshObject(data) {
    var meshObject = new MeshObject();
    meshObject.cameraSetUp = new CameraSetUp(vectorFromData(data["cameraSetUp"]["position"]),
        vectorFromData(data["cameraSetUp"]["lookAt"]),
        vectorFromData(data["cameraSetUp"]["rotation"]));
    meshObject.index = data["index"];
    return meshObject;
}

function MeshFile(filename, objects, cameraPosition) {
    this.filename = filename;
    this.objects = objects;
    this.cameraPosition = cameraPosition;
}

// function createMeshFile(data) {
//     var meshFile = new MeshFile();

//     meshFile.filename = data["filename"];
////     console.log(data["filename"]);
//     meshFile.cameraPosition = vectorFromData(data["camera_position"]);
////     console.log("meshfile cam position");
////     console.log(meshFile.cameraPosition);
//     var meshObjects = [];
//     var j;
//     for (j  = 0; j < data["objects"].length; j++) {
//         meshObjects.push(createMeshObject(data["objects"][j]));
//     }
//     meshFile.objects = meshObjects;
//     return meshFile;
// }

function createMeshFile(data) {
    var meshFile = new MeshFile();
    meshFile.filename = data["filename"];
    meshFile.objects = [];
    return meshFile;
}

function createMeshFileFromFilename(filename) {
    var meshFile = new MeshFile();
    meshFile.filename = filename
    meshFile.objects = [];
    return meshFile;
}

MeshFile.prototype.meshObjectForIndex = function(index) {

    //TODO: remove this line once we have camera info
    var cameraSetup = new CameraSetUp(THREE.Vector3(), THREE.Vector3(), THREE.Vector3());
    return new MeshObject(cameraSetup,index);

    //for (var i = 0; i < this.objects.length; i++) {
    //    if (this.objects[i].index == index) {
    //        return this.objects[i];
    //    }
    //}
};

function LabelObjectMapFile(filename, indices) {
    this.filename = filename;
    this.indices = indices;
}

function LabelObjectMap(label, data, color) {
    this.label = label;
    this.color = color;
    this.files = [];
    for (var i = 0; i < data["files"].length; i ++) {
        this.files.push(new LabelObjectMapFile(data["files"][i]["filename"], data["files"][i]["indices"]));
    }
}

function LabelsManager(modelname, labelcolor, labelLoadCompletionHandler ) {
    this.objects= [];
    this.labelObjectMap = [];
    this.labelcolor = labelcolor;
    this.modelname = modelname;
    var thisPointer = this;
//    console.log(modelname);

    thisPointer.objects.push(createMeshFileFromFilename(modelname));
    $.getJSON("get_label_info_json.php", function(data) {
//        console.log("get label info json");
//        console.log(data);
        for(var key in data) {
            if (data.hasOwnProperty(key)) {
                thisPointer.labelObjectMap.push(new LabelObjectMap(key, data[key], labelcolor[key]));
            }
        }
        if (labelLoadCompletionHandler) {
            labelLoadCompletionHandler(thisPointer);
        }
    });
}

LabelsManager.prototype.incrementNumSkips = function(userid, callback) {
  $.getJSON('update_get_userinfo.php',{'userid' : userid,'isnumskip' : '1'}, function(data) {
       callback(data); 
    });
}

LabelsManager.prototype.updatePercent = function(userid, percent, callback) {
  $.post('update_get_userinfo.php',
    {
        'userid' : userid,
        'percent' : percent
    },
    function(data) {
       callback(data); 
    });
}

LabelsManager.prototype.getUnlabelledObjects = function( totalnumobjects, surfacearea, currworker, isadmin, workerId, assignmentId, hitId, callback){
    var index = -1;
    var returnkey = -1;
    $.post('get_labelled_objects.php', {'modelname': this.modelname,'getlabel':'0', 'currworker':currworker, 'isadmin':isadmin, 'workerId': workerId, 'assignmentId':assignmentId, 'hitId':hitId}, function(data){
        for(var i =0; i < surfacearea.length; i++){
            if(surfacearea[i] === undefined)
                continue;

            key = parseInt(surfacearea[i][0]);
            //if(interiorobjindex.includes(key.toString()) || data.includes(key)){
            if( data.includes(key)){
                continue;
            }
            else{
                index = i;
                returnkey = key
                break;
            }
        }
        result = {"index":index, "key":returnkey}
        callback(result);
    });

}

//LabelsManager.prototype.admingetPreviouslyLabelledObjects = function(currworker, callback){
////    console.log(currworker);
//    $.post('get_labelled_objects.php', {'modelname': this.modelname,'getlabel':'1', 'currworker':currworker, 'isadmin':true}, function(data){
////        console.log(data);
//        result = {"data":data};
//        callback(result);
//    });
//}

LabelsManager.prototype.getPreviouslyLabelledObjects = function(currworker, isadmin, workerId, assignmentId, hitId, callback){
    $.post('get_labelled_objects.php', {'modelname': this.modelname,'getlabel':'1', 'currworker':currworker, 'isadmin':isadmin, 'workerId': workerId, 'assignmentId':assignmentId, 'hitId':hitId}, function(data){
//		console.log(data);
		result = {"data":data};
		callback(result);
    });
}


LabelsManager.prototype.colorForLabel = function(label) {
    return this.labelcolor[label];
};

LabelsManager.prototype.labelForMeshObjectAtIndex = function(filename, objIndex) {
//    //console.log(filename);
//    //console.log(this.labelObjectMap);
    for (var i = 0; i < this.labelObjectMap.length; i++) {
        var map = this.labelObjectMap[i];
//        //console.log(map);
        for (var j = 0; j < map.files.length; j++) {
            var file = map.files[j];
//            //console.log(file);
            if (filename == file.filename && ($.inArray(objIndex, file.indices) > -1)) {
                return map.label;
            }
        }
    }
};


LabelsManager.prototype.labelsForFile = function(filename) {

    var labels = [];
    for (var i = 0; i < this.labelObjectMap.length; i++) {
        for (var j = 0; j < this.labelObjectMap[i].files.length; j++) {
            if (this.labelObjectMap[i].files[j].filename == filename) {
                labels.push(this.labelObjectMap[i].label);
            }
        }
    }
    return labels;
};

LabelsManager.prototype.doesFileContainLabel = function(filename, label) {
    for (var i = 0; i < this.labelObjectMap.length; i++) {
        if (this.labelObjectMap[i].label == label) {
            for (var j = 0; j < this.labelObjectMap[i].files.length; j++) {
                if (this.labelObjectMap[i].files[j].filename == filename) {
                    return true;
                }
            }
        }
    }
    return false;
};

LabelsManager.prototype.meshObjectForIndex = function(filename, objIndex) {
    var mesh = this.meshOfFileName(filename);
    if (mesh) {
        return mesh.meshObjectForIndex(objIndex);
    }
    return null;
};

LabelsManager.prototype.meshObjectsForLabel = function(filename, label) {
    var indices = [];
    var objs = [];
    for (var i = 0; i < this.labelObjectMap.length; i++) {
        if (this.labelObjectMap[i].label == label) {
            for (var j = 0; j < this.labelObjectMap[i].files.length; j++) {
                if (this.labelObjectMap[i].files[j].filename == filename) {
                    indices = this.labelObjectMap[i].files[j].indices;
                }
            }
        }
    }

    if (indices.length > 0) {
        var mesh = this.meshOfFileName(filename);
        for (i = 0; i < indices.length; i++) {
            objs.push(mesh.meshObjectForIndex(indices[i]))
        }
        return objs;
    }
    else {
        return [];
    }
};

LabelsManager.prototype.meshOfFileName = function(filename) {
    for (var i = 0; i < this.objects.length; i++) {
        if (this.objects[i].filename == filename) {
            return this.objects[i];
        }
    }
};

LabelsManager.prototype.removeLabelForIndices = function(userid, filename, indices, objnames, onFinish) {
    var thisPointer = this;
    var num_cannot_label = 0;

    $.post("update_label_json.php",
    {
        filename: filename,
        label : "none",
        userid : userid,
        objnames: JSON.stringify(objnames),
        indices : JSON.stringify(indices)
    },
     function (data) {
//        console.log(data);
        var actualindicesToupdate = [];
        if (data == 'success') {
            for (i = thisPointer.labelObjectMap.length - 1; i >= 0; i --) {
                var shouldDelete = true;
                for (j = 0; j < thisPointer.labelObjectMap[i].files.length; j++) {
                    if(thisPointer.labelObjectMap[i].files[j].filename == filename){
                        for(k=0; k<thisPointer.labelObjectMap[i].files[j].indices.length; k++){
                            if(indices.includes(thisPointer.labelObjectMap[i].files[j].indices[k]))
                            {
//                                console.log("deleteing indices from label object map");
//                                console.log(thisPointer.labelObjectMap[i].files[j].indices[k]);
                                actualindicesToupdate.push(thisPointer.labelObjectMap[i].files[j].indices[k]);
                                if(thisPointer.labelObjectMap[i].label == "cannot_label")
                                    num_cannot_label += 1;
                                thisPointer.labelObjectMap[i].files[j].indices.splice(k, 1);
                                k--;
                            }
                        }
                    }
                   
                }
                
            }
             //If there are any label which was made empty, remove it.
            for (i = thisPointer.labelObjectMap.length - 1; i >= 0; i --) {
                var shouldDelete = true;
                for (j = 0; j < thisPointer.labelObjectMap[i].files.length; j++) {
                    if (thisPointer.labelObjectMap[i].files[j].indices.length > 0) {
                        shouldDelete = false;
                    }
                }
                if (shouldDelete) {
//                    console.log("should delete");
                    thisPointer.labelObjectMap.splice(i, 1);
                    i--;
                }
            }
        }
        if (onFinish) {
                data = {"status":data, "num_cannot_label":num_cannot_label, "indices":actualindicesToupdate}
                onFinish(data);
            }
        }
    );
};

LabelsManager.prototype.updateLabelForIndices = function(userid, filename, indices, objnames, newLabel, onFinish) {
//        console.log(this.labelObjectMap.length);
	for (var i = 0; i < this.labelObjectMap.length; i ++) {
	    for (var j = 0; j < this.labelObjectMap[i].files.length; j ++) {
		if (this.labelObjectMap[i].files[j].filename == filename) {
		    this.labelObjectMap[i].files[j].indices = this.labelObjectMap[i].files[j].indices.filter(function (index) {
			return ($.inArray(index, indices) <= -1);
		    });
		}
	    }
	}
	//check if the newLabel already exists if yes,
	var labelToObjectMap = null;
	for (i = 0; i < this.labelObjectMap.length; i ++) {
	    if (this.labelObjectMap[i].label == newLabel) {
		labelToObjectMap = this.labelObjectMap[i];
		break;
	    }
	}
	if (labelToObjectMap) {
	    // insert the indices to the labelObjectMap

	    //see if the label is already set in this file.
	    var labelObjectMapFile = null;
	    for (j = 0; j < labelToObjectMap.files.length; j ++) {
		if (labelToObjectMap.files[j].filename == filename) {
		    labelObjectMapFile = labelToObjectMap.files[j];
		    break;
		}
	    }
	    //if yes, then insert indices
	    if  (labelObjectMapFile) {
		this.labelObjectMap[i].files[j].indices = this.labelObjectMap[i].files[j].indices.concat(indices);
	    }
	    else{
		labelObjectMapFile = new LabelObjectMapFile(filename, indices);
		this.labelObjectMap[i].files.push(labelObjectMapFile);
	    }
	}
	else { //if newLabel does not present,

	    // create a new labelObjectMap and insert.
	    labelObjectMapFile = new LabelObjectMapFile(filename, indices);
	    labelToObjectMap = new LabelObjectMap(newLabel,{
		"color" : this.labelcolor[newLabel],
		"files" : []
	    });
	    labelToObjectMap.files.push(labelObjectMapFile);
	    this.labelObjectMap.push(labelToObjectMap);
	}

	//If there are any label which was made empty, remove it.
	for (i = this.labelObjectMap.length - 1; i >= 0; i --) {
	    var shouldDelete = true;
	    for (j = 0; j < this.labelObjectMap[i].files.length; j++) {
		if (this.labelObjectMap[i].files[j].indices.length > 0) {
		    shouldDelete = false;
		}
	    }
	    if (shouldDelete) {
		this.labelObjectMap.splice(i, 1);
                i--;
	    }
	}
}
LabelsManager.prototype.getDistinctLabels = function(workerId, onFinish) {
    //console.log(workerId);
    $.post("find_distinct_labels.php",
        {
            workerId : workerId,
        },
        function (data) {
            if (onFinish) {
                onFinish(data);
            }
        });
}
LabelsManager.prototype.setLabelForIndices = function(userid, filename, indices, objnames, newLabel, onFinish) {
    var thisPointer = this;
//    console.log(indices);
    $.post("update_label_json.php",
        {
            filename: filename,
            label : newLabel,
            userid : userid,
            objnames: JSON.stringify(objnames),
            indices : JSON.stringify(indices)
        },
        function (data) {
            if (data == 'success') {

                //remove indices from Label map
                for (var i = 0; i < thisPointer.labelObjectMap.length; i ++) {
                    for (var j = 0; j < thisPointer.labelObjectMap[i].files.length; j ++) {
                        if (thisPointer.labelObjectMap[i].files[j].filename == filename) {
                            thisPointer.labelObjectMap[i].files[j].indices = thisPointer.labelObjectMap[i].files[j].indices.filter(function (index) {
                                return ($.inArray(index, indices) <= -1);
                            })
                        }
                    }
                }

                //check if the newLabel already exists if yes,
                var labelToObjectMap = null;
                for (i = 0; i < thisPointer.labelObjectMap.length; i ++) {
                    if (thisPointer.labelObjectMap[i].label == newLabel) {
                        labelToObjectMap = thisPointer.labelObjectMap[i];
                        break;
                    }
                }
                if (labelToObjectMap) {
                    // insert the indices to the labelObjectMap

                    //see if the label is already set in this file.
                    var labelObjectMapFile = null;
                    for (j = 0; j < labelToObjectMap.files.length; j ++) {
                        if (labelToObjectMap.files[j].filename == filename) {
                            labelObjectMapFile = labelToObjectMap.files[j];
                            break;
                        }
                    }
                    //if yes, then insert indices
                    if  (labelObjectMapFile) {
                        thisPointer.labelObjectMap[i].files[j].indices = thisPointer.labelObjectMap[i].files[j].indices.concat(indices);
                    }
                    else{
                        labelObjectMapFile = new LabelObjectMapFile(filename, indices);
                        thisPointer.labelObjectMap[i].files.push(labelObjectMapFile);
                    }
                }
                else { //if newLabel does not present,

                    // create a new labelObjectMap and insert.
                    labelObjectMapFile = new LabelObjectMapFile(filename, indices);
                    labelToObjectMap = new LabelObjectMap(newLabel,{
                        "color" : thisPointer.labelcolor[newLabel],
                        "files" : []
                    });
                    labelToObjectMap.files.push(labelObjectMapFile);
                    thisPointer.labelObjectMap.push(labelToObjectMap);
                }

                //If there are any label which was made empty, remove it.
                for (i = thisPointer.labelObjectMap.length - 1; i >= 0; i --) {
                    var shouldDelete = true;
                    for (j = 0; j < thisPointer.labelObjectMap[i].files.length; j++) {
                        if (thisPointer.labelObjectMap[i].files[j].indices.length > 0) {
                            shouldDelete = false;
                        }
                    }
                    if (shouldDelete) {
                        thisPointer.labelObjectMap.splice(i, 1);
                        i--;
                    }
                }
            }
            if (onFinish) {
                onFinish(data);
            }
        }
    );
};



