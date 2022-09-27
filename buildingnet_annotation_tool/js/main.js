/**
 * Created by rajendrahn on 03/02/16
 */

var renderView = null;
var renderView_texture = null;
var labelManager = null;
var floatingDiv = null;
var catlabel = null;
var catlabelall = null;
var catlabellength = 0;
var catindex = 0;
var category = null;
var label = "";
var surfacearea = [];
var lastunselectedIndex = -1;
var surfaceareaindex = -1;
var skippedIndex = [];
var totalsurfacearea = 0;
var currmodel = "";
var surfacearealabelled = 0.0;
var wireframeindices = [];
var objidslabelled = [];
var cannot_label = 0;

var facedata = [];
var zoomfiles = [];

$(document).ready(function () {

    category = document.getElementById('category').getAttribute('value');
    currmodel = document.getElementById('model').getAttribute('value');
    document.getElementById('skip').blur();

    if(category.length <= 0)
        category = getCategory(currmodel);


    var offsets_color = document.getElementById('container-color').getBoundingClientRect();
    var offsets_texture = document.getElementById('container-texture').getBoundingClientRect();
//    console.log(offsets_color);
   
    renderView = new View(document.getElementById("container-color"),new Frame(offsets_color.top, offsets_color.left, offsets_color.width, offsets_color.height ));
    renderView_texture = new View(document.getElementById("container-texture"),new Frame(offsets_color.top , offsets_texture.left, offsets_texture.width, offsets_texture.height));

    $.getJSON("js/allfacesdata.json",function(data){
            facedata = data["faces"][currmodel];
    });
    $.getJSON("js/zoomfiles.json",function(data){
            zoomfiles = data;
    });

    window.addEventListener('resize', onWindowResize, false);
    renderView.renderer.domElement.addEventListener('mousemove', onMouseMove, false);
    renderView.renderer.domElement.addEventListener('mousedown', onMouseDown, false);
    renderView.renderer.domElement.addEventListener('mouseup', onMouseUp, false);
    renderView.renderer.sortObjects = false;

    window.addEventListener('keydown', onKeyDown, false);
    window.addEventListener('keyup', onKeyUp, false);

    catlabel = categoryjs[category+'_1'];
    catlabelall = categoryjs[category];
    catlabellength = catlabel.length;// - 1;
//    if(category != "STADIUM")
//    {
//        catlabel = catlabel.concat(categoryjs["LANDSCAPE"]);
//        if(category == "INDUSTRIAL" || category == "AGRICULTURAL"){
//            catlabel.push("bridge");
//        }
//    }
    var labelcolor = categoryjs['COLORS'];
    catindex = 0;

//    //console.log(catlabel);

    function show(id, value) {
        document.getElementById(id).style.display = value ? 'block' : 'none';
    }

    show('loading', true);
    labelManager = new LabelsManager(currmodel, categoryjs['COLORS'], function(){
        var obj = labelManager.objects[0];
//        //console.log(obj.filename)
        if(category.length <= 0)
             category = getCategory(obj.filename);

        
        loadMesh(obj);
        loadAllLabelData();

    });

    function getCategory(filename){
//       //console.log(filename);
       var cat =""
       var allcat = categoryjs['allcategory']
//       //console.log(allcat);
       for(var i=0; i<allcat.length; i++){
           if (filename.includes(allcat[i])){
               cat = allcat[i];
               break
           }
       } 
       return cat
    }


function copy(o) {
   var output, v, key;
   output = Array.isArray(o) ? [] : {};
   for (key in o) {
       v = o[key];
       output[key] = (typeof v === "object") ? copy(v) : v;
   }
   return output;
}

    function loadMesh(obj) {
        renderView.showMesh(obj.filename, function (err) {
        if (err) {
            show('loading', false);
            return
        }
        var j = renderView.scene.toJSON();
        try {
            
            for(var i =0; i< renderView.objs.length; i++)
                renderView_texture.objs.push(copy(renderView.objs[i]));

        } catch(err) {
//            //console.log("in catch");
//            //console.log(err);
            renderView_texture.showMesh(obj.filename, function (err) {
            if (err) {
                show('loading', false);
                return
            }
            
            //renderView_texture.changetextureMaterialColor();
            });
        }


//        var exporter = new THREE.OBJExporter();
//        var result = exporter.parse(renderView.rootObj);
//        var blob = new Blob( [result], {type: 'text/plain'});
//        var link = document.createElement('a');
//        link.style.display  = 'none';
//        document.body.appendChild(link);
//
//        link.href = URL.createObjectURL(blob);
//        link.download = 'test.obj';
//        link.click();
//

        renderView.SetColor();
        renderView.changeMaterialColor();
        renderView.getBoundingBoxScene();

//        //console.log(renderView.center);

        renderView.updateCamera();
        
        renderView_texture.camera = renderView.camera;

        renderView.controls.target = renderView.center;
        renderView.controls.update();

        surfacearea = Object.keys(renderView.surfacearea).map(function(key) {
           return [key, renderView.surfacearea[key]];
        });
    
       // Sort the array based on the second element
       surfacearea.sort(function(first, second) {
          return second[1] - first[1];
       });

       
       for(var i=0; i<surfacearea.length; i++){
        //if(!renderView.interior.includes(i.toString()))
        //{
            totalsurfacearea += renderView.surfacearea[i];
        //}
       }

//        //console.log("****** getting previously labelled"); 
        var labelsForFile = labelManager.labelsForFile(labelManager.objects[0].filename);
        for (var i = 0; i < labelsForFile.length; i++) {
            var meshObjs = labelManager.meshObjectsForLabel(labelManager.objects[0].filename, labelsForFile[i]);
            var color = labelManager.colorForLabel(labelsForFile[i]);
            renderView.colorObjectAtIndices(color, meshObjs.map(function(obj) {return obj.index;}));
        }
        
//        //console.log("getting previously labelled"); 
        getPreviouslyLabelledObjects();
//        //console.log(surfacearealabelled);
        show('loading', false);
         document.getElementById('admin_exteriorcomponents').innerHTML = String(renderView.exterior)+" components::"+String(facedata)+" faces";
        });



    }

    function syncSidePanel(objLabel) {
        var filename = renderView.current_filename;
        var labels = labelManager.labelsForFile(filename);
        var collbutton = document.getElementById("mesh_" + filename);

        var content = collbutton.nextElementSibling;
        $(content).find("ul").append('<li class="w3-padding-12"><button class="w3-button w3-padding-small w3-hover-black" style="margin-left:10px" value="'+objLabel+'">'+objLabel+'</button></div></li>');

        collbutton.classList.add("active");

        content.style.maxHeight = content.scrollHeight + "px";
    }

    $("#label_form").submit(function(e) {
        e.preventDefault();
       document.getElementById("submit").blur();
       if(document.getElementById("issubmit").value == 0) {
       
        var indices = renderView.indicesOfSelectedObjs();
        var objnames = new Array(indices.length);
        objnames.fill("",0, indices.length);// renderView.objnameOfSelectedObjs();
        var filename = renderView.current_filename;
        var objLabel =  label;
        var userid = $("#userid").val();
        var workerId = $("#workerId").val();
       } else {
         document.getElementById("issubmit").value = 0;
         indices = undefined;
       }

        if(indices !== undefined && objLabel !== undefined){
            if (indices.length > 0 && objLabel.length > 0) {
                if(objLabel == "cannot_label"){
                    cannot_label += indices.length;
                    if(cannot_label > 5) {
                        issue_warning(cannot_label);
                    }
                }
                var labels = labelManager.labelsForFile(filename);
                labelManager.setLabelForIndices(userid, filename, indices, objnames, objLabel, function (data) {

                    if (data != 'success') {
                        if (data != 'You had already labeled this object(s).') {
                            alert("Something went wrong. Could not save the label. Error: " + data);
                        }
                    }
                    else {
                        $("#submit_confirm_span").fadeIn("slow");
//                        //console.log(indices.length);
//                        //console.log(totalsurfacearea);
//                        console.log(surfacearealabelled);
                        for(var i=0; i<indices.length; i++){
                            //if(!renderView.interior.includes(indices[i].toString()) && !objidslabelled.includes(indices[i])){
                            if(!objidslabelled.includes(indices[i])){
                                objidslabelled.push(indices[i]);
                                surfacearealabelled += renderView.surfacearea[indices[i].toString()];
                            }
                        }
                        if(totalsurfacearea <= 0) {
				surfacearea = Object.keys(renderView.surfacearea).map(function(key) {
				   return [key, renderView.surfacearea[key]];
				});
			    
			       // Sort the array based on the second element
			       surfacearea.sort(function(first, second) {
				  return second[1] - first[1];
			       });

			       
			       for(var i=0; i<surfacearea.length; i++){
				    totalsurfacearea += renderView.surfacearea[i];
			       }
                        }
                        var complete = Math.round(surfacearealabelled*100.0/totalsurfacearea*1.0);
                        document.getElementById('exteriorcomponents').innerHTML = String(complete)+"% complete"
                        updatePercent(complete);
                        if(complete >= 70) {
                            document.getElementById("rewritehit").value=1;
                            document.getElementById("bonuslabel").style.visibility="visible";
                        } else {
                            document.getElementById("bonuslabel").style.visibility="hidden";
                        }
//	                console.log(document.getElementById("rewritehit").value);
                        if(objLabel){
                            renderView.colorObjectAtIndices( labelcolor[objLabel],
                            labelManager.meshObjectsForLabel(filename, objLabel).map(function (obj) {
                                return obj.index;
                            }));
                        }
                    }
                });

                labelManager.getDistinctLabels(workerId, function(data) {
                        document.getElementById('distinct_labels').value = parseInt(data);
                });
            }
        }
        else if (indices.length > 0){
//            console.log("indices greater");
            var nextIndex = (indices[0] + 1) % renderView.cameraInfo.length;
            renderView.showObjectAtIndices([nextIndex], true);
        }
    });

    $("#export_OBJ").on('click', function(){
        var exporter = new THREE.OBJExporter ();
        var result = exporter.parse (renderView.scene);
        floatingDiv.style.display = 'block';
        floatingDiv.innerHTML = result.split ('\n').join ('<br />');
    });

    render();
 
});

function removeUnusedLabel(){
        var filename = renderView.current_filename;
        var labels = labelManager.labelsForFile(filename);

        var content = document.getElementById("mesh_" + filename).nextElementSibling;
        var lis = $(content).find("ul li");
        for(var i=0; li=lis[i]; i++) {
            var val = li.querySelectorAll("button")[0].value;
            if(!labels.includes(val)) {
                li.parentNode.removeChild(li);
            }
        }
    }


function loadLabelData(bothmode=false) {
     
    var labelbutton =  $('#labels_list > div');
    var nextvalue = $('#labels_list > div > div');

     if(nextvalue != undefined){
        nextvalue.remove();
    }

    var list = $('#labels_list > ul');
    var lilength = $('#labels_list ul li').length;
    
    if(lilength > 0){
        list.empty();
    }
 
    document.getElementById("container-color").style.width  = "62%";
    document.getElementById("labels_list").style.width ="2%";
    document.getElementById("container-texture").style.width = "36%";

    //if(catindex == catlabellength)
    //    catindex--;
    var data = catlabel[catindex];//categoryjs[category][catindex];
    if(data === undefined) {
        catindex--;
        data = catlabel[catindex];
    }
    if(catindex == 0) {
        document.getElementById("nextbutton").style.visibility ="visible";
        document.getElementById("prevbutton").style.visibility ="hidden";
    } else if(catindex == catlabel.length-1) {
        document.getElementById("nextbutton").style.visibility ="hidden";
        document.getElementById("prevbutton").style.visibility ="visible";
    } else {
        document.getElementById("nextbutton").style.visibility ="visible";
        document.getElementById("prevbutton").style.visibility ="visible";
    }
    label = data;
    //var labelcolor = {"Floor":"#ff3333", "Door":"#1a53ff", "Roof":"#d11aff", "Window":"#4775d1", "Wall":"#ff3399"};
    var labelcolor = categoryjs['COLORS'];
    var labellink = categoryjs['LINKS'];
    var labelbutton =  $('#single_label');
    var nextvalue = $('#single_label > #labelinfo1');
    if(nextvalue != undefined){
        nextvalue.remove();
    }
    var nextvalue = $('#single_label > #labelinfo2');
    if(nextvalue != undefined){
        nextvalue.remove();
    }
    var splitlabel = data.replace("/","_");
    var vowel = categoryjs["VOWEL"][data];
    labelbutton.prepend('<div id="labelinfo1" style="font-size:8"><b>Select all <div style="padding:0px; display:inline-block; background-color:'+labelcolor[data]+'"><div class="w3-padding-small w3-hover-black" style="margin-left:25px; margin-right:25px; font-weight:bold; background-color:black; color:white; value='+data+'"><a id="labellink" onclick="blurlabellink()" href="links.php?label='+splitlabel+'" target ="_blank">'+ data.toUpperCase() + '</a></div></div> components, then press enter</b></div><div id="labelinfo2" style="font-size:5; color:green"><b> If you do not know what '+vowel+' '+data+' is, click <a id="labellink" style="color:blue;" onclick="blurlabellink()" href="links.php?label='+splitlabel+'" target="_blank"> here </a> for help</b></div>');

   if(bothmode){
     
    document.getElementById("container-color").style.width  = "56%";
    document.getElementById("labels_list").style.width ="8%";
    document.getElementById("container-texture").style.width = "36%";
    document.getElementById("unlabelled").style.visibility = "visible";
    document.getElementById("unlabelled").style.float = "right";
    //document.getElementById("skip").style.visibility = "hidden";
    document.getElementById("submit").style.visibility = "visible";
 

    var labelbutton =  $('#labels_list > div');
    var nextvalue = $('#labels_list > div > div');

     if(nextvalue != undefined){
        nextvalue.remove();
    }
    var list = $('#labels_list > ul');
    var lilength = $('#labels_list ul li').length;
    
            //list.append('<li style="padding:0px; background-color:'+labelcolor[catlabelall[i]]+'"><button class="w3-button w3-padding-small w3-hover-black" style="margin-left:10px; font-weight:regular; font-size:11px; padding-top:0px; padding-bottom:0px;background-color:black; color:white;"; value='+catlabelall[i]+'>'+ catlabelall[i] + '</button></li>');
    if(lilength <= 0){
        
        for (var i = 0; i < catlabelall.length; i++) 
            list.append('<li style="padding:0px; background-color:'+labelcolor[catlabelall[i]]+'"><button class="w3-button w3-padding-small w3-hover-black" style="margin-left:10px; font-weight:regular; font-size:11px; height:21.5px; padding-top:0px; background-color:black; color:white;"; value='+catlabelall[i]+'>'+ catlabelall[i] + '</button></li>');
        
    }
    $('#labellink').blur();

    $('#labels_list > ul > li >  button').on('click',function (e) {
        e.preventDefault();
//        console.log(this.value);
        this.blur();
        label = this.value;
        var labelbutton =  $('#single_label');
        var nextvalue = $('#single_label > #labelinfo1');
        if(nextvalue != undefined){
            nextvalue.remove();
        }
        var nextvalue = $('#single_label > #labelinfo2');
        if(nextvalue != undefined){
            nextvalue.remove();
        }
        var splitlabel = label.replace("/","_");
        var vowel = categoryjs["VOWEL"][label];

        labelbutton.prepend('<div id="labelinfo1" style="font-size:8"><b>Select all <div style="padding:0px; display:inline-block; background-color:'+labelcolor[label]+'"><div class="w3-padding-small w3-hover-black" style="margin-left:25px; margin-right:25px; font-weight:bold; background-color:black; color:white; value='+label+'"><a id="labellink" onclick="blurlabellink()" href="links.php?label='+splitlabel+'" target="_blank">'+ label.toUpperCase() + '</a></div></div> components, then press enter</b></div><div id="labelinfo2" style="font-size:5; color:green"><b> If you do not know what '+vowel+' '+label+' is click <a id="labellink" onclick="blurlablelink()" style="color:blue;" href="links.php?label='+splitlabel+'" target="_blank"> here </a> for help</b></div>');

        for (var i = 0; i < catlabellength; i++) 
        {
            if(catlabel[i] == label){
                catindex = i;
                break;
            }
        }
        document.getElementById("nextbutton").style.visibility ="hidden";
        document.getElementById("prevbutton").style.visibility ="hidden";
        if(catindex == catlabellength-1){
            document.getElementById("prevbutton").style.visibility ="visible";
        }
        else if(catindex == 0) {
            document.getElementById("nextbutton").style.visibility ="visible";
        }
        else if(catindex > 0 && catindex < catlabellength-1) {
            document.getElementById("nextbutton").style.visibility ="visible";
            document.getElementById("prevbutton").style.visibility ="visible";
        }
        if(lastunselectedIndex != -1)
        {
        renderView.unlabelledAddToSelectedObs([lastunselectedIndex]);
        lastunselectedIndex = -1;
        }
    });
   }


}

function loadAllLabelData() {

    var data = categoryjs[category];
    label = data;
    var labelcolor = categoryjs['COLORS'];
    var labellink = categoryjs['LINKS'];
    var labelbutton =  $('#single_label');
    var nextvalue = $('#single_label > #labelinfo1');
    if(nextvalue != undefined){
        nextvalue.remove();
    }

    var nextvalue = $('#single_label > #labelinfo2');
    if(nextvalue != undefined){
        nextvalue.remove();
    }
    labelbutton.prepend('<div id="labelinfo1" style="font-size:8"><b>For labeling changes: Click any label from the list below, then press enter</b></div><div id="labelinfo2" style="font-size:5; color:green"><b>When you are >=70% done, you can submit the task on the bottom of the page</b></div>')

    var labelbutton =  $('#labels_list > div');
    var nextvalue = $('#labels_list > div > div');
//    console.log(nextvalue);

     if(nextvalue != undefined){
        nextvalue.remove();
    }
 
    document.getElementById("container-color").style.width  = "56%";
    document.getElementById("labels_list").style.width ="8%";
    document.getElementById("container-texture").style.width = "36%";
    document.getElementById("unlabelled").style.visibility = "visible";
    document.getElementById("unlabelled").style.float = "right";
    document.getElementById("showalllabel").style.visibility = "hidden"
    document.getElementById("showalllabel").style.float = "none";
    document.getElementById("showonelabel").style.visibility = "visible"
    document.getElementById("showonelabel").style.float = "right";
    document.getElementById("submit").style.visibility = "visible";
 
    document.getElementById("nextbutton").style.visibility ="hidden";
    document.getElementById("prevbutton").style.visibility ="hidden";

    var list = $('#labels_list > ul');
    var lilength = $('#labels_list ul li').length;
    
    if(lilength <= 0){
        
        for (var i = 0; i < catlabelall.length; i++) 
            list.append('<li style="padding:0px; background-color:'+labelcolor[catlabelall[i]]+'"><button class="w3-button w3-padding-small w3-hover-black" style="margin-left:10px; font-size:11px; font-weight:regular; padding-top:0px; height:21.5px;background-color:black; color:white;"; value='+catlabelall[i]+'>'+ catlabelall[i] + '</button></li>');
        
        //document.getElementById("nextbutton").style.visibility ="hidden";
        //document.getElementById("prevbutton").style.visibility ="hidden";
    }

    $('#labellink').blur();
    $('#labels_list > ul > li >  button').on('click',function (e) {
        e.preventDefault();
//        console.log(this.value);
        this.blur();
        label = this.value;
        var labelbutton =  $('#single_label');
        var nextvalue = $('#single_label > #labelinfo1');
        if(nextvalue != undefined){
            nextvalue.remove();
        }
        var nextvalue = $('#single_label > #labelinfo2');
        if(nextvalue != undefined){
            nextvalue.remove();
        }
        var splitlabel = label.replace("/","_");
        var vowel = categoryjs["VOWEL"][label];

        labelbutton.prepend('<div id="labelinfo1" style="font-size:8"><b>Select all <div style="padding:0px; display:inline-block; background-color:'+labelcolor[label]+'"><div class="w3-padding-small w3-hover-black" style="margin-left:25px; margin-right:25px; font-weight:bold; background-color:black; color:white; value='+label+'"><a id="labellink" onclick="blurlabellink()" href="links.php?label='+splitlabel+'" target="_blank">'+ label.toUpperCase() + '</a></div></div> components, then press enter</b></div><div id="labelinfo2" style="font-size:5; color:green"><b> If you do not know what '+vowel+' '+label+' is click <a id="labellink" onclick="blurlabellink()" style="color:blue;" href="links.php?label='+splitlabel+'" target="_blank"> here </a> for help</b></div>');

        for (var i = 0; i < catlabellength; i++) 
        {
            if(catlabel[i] == label){
                catindex = i;
                break;
            }
        }
//        console.log(catindex);
//        console.log(catlabel.length-1);
        if(catindex < catlabel.length-1) {
            document.getElementById("nextbutton").style.visibility ="visible";
            document.getElementById("nextbutton").style.visibility ="hidden";
        }
        if(catindex == 0 ) {
            document.getElementById("nextbutton").style.visibility ="visible";
            document.getElementById("prevbutton").style.visibility ="hidden";
        }
        if(catindex > 0 && catindex < catlabel.length -1) {
            document.getElementById("nextbutton").style.visibility ="visible";
            document.getElementById("prevbutton").style.visibility ="visible";
        }
        if(lastunselectedIndex != -1)
        {
        renderView.unlabelledAddToSelectedObs([lastunselectedIndex]);
        lastunselectedIndex = -1;
        }
    });

}


function render() {
    requestAnimationFrame(render);
    renderView.render();
    renderView_texture.render();
}

function selectParent()
{
    document.getElementById("parent").blur();
    renderView.selectParent();
    var indices = renderView.indicesOfSelectedObjs();
    addWireFrame(indices);
}

function selectChildren()
{
    document.getElementById("children").blur();
    renderView.selectChildren();
    removeWireFrame();
    var indices = renderView.indicesOfSelectedObjs();
    addWireFrame(indices);
}

function selectSimilar()
{
    document.getElementById("similar").blur();
    renderView.selectSimilar();
    var indices = renderView.indicesOfSelectedObjs();
    addWireFrame(indices);
}

function resetView()
{
    document.getElementById("reset").blur();
    renderView.resetView();
}

function issue_warning(count)
{
    alert("You have labelled "+count.toString()+ " parts as cannot label");
}

function previousFunction(){
    if(catindex == catlabellength){
        catindex--;
        if(document.getElementById("showalllabel").style.visibility == "hidden")
            loadLabelData(true);
        else
            loadLabelData();
        
        document.getElementById("nextbutton").style.visibility ="visible";
    }
    else if(catindex > 0){
        document.getElementById("nextbutton").style.visibility ="visible";
        catindex--;
        if(document.getElementById("showalllabel").style.visibility == "hidden")
            loadLabelData(true);
        else
            loadLabelData();
    }
    document.getElementById("prevbutton").blur();
    document.getElementById("nextbutton").blur();
}

function nextFunction(){
    if(catindex == 0) {
        document.getElementById("prevbutton").style.visibility ="visible";
    }
    if(catindex < catlabel.length-1){
        catindex++;
        if(document.getElementById("showalllabel").style.visibility == "hidden")
            loadLabelData(true);
        else
            loadLabelData();
    }
    else if(catindex == catlabellength-1){
        document.getElementById("nextbutton").style.visibility ="hidden";
        document.getElementById("showalllabel").style.visibility = "hidden"
        document.getElementById("showalllabel").style.float = "none";
        document.getElementById("showonelabel").style.visibility = "visible"
        document.getElementById("showonelabel").style.float = "right";
        loadAllLabelData();
        catindex++;
    }
    document.getElementById("prevbutton").blur();
    document.getElementById("nextbutton").blur();
}


function showAllLabelFunction() {
    document.getElementById("prevbutton").blur();
    document.getElementById("nextbutton").blur();
    document.getElementById("showalllabel").blur();
    document.getElementById("showonelabel").blur();
    document.getElementById("showalllabel").style.visibility = "hidden";
    document.getElementById("showalllabel").style.float = "none";
    document.getElementById("showonelabel").style.visibility = "visible";
    document.getElementById("showonelabel").style.float = "right";
    loadAllLabelData();
}

function showOneLabelFunction() {
    document.getElementById("prevbutton").blur();
    document.getElementById("nextbutton").blur();
    document.getElementById("showalllabel").blur();
    document.getElementById("showonelabel").blur();
    document.getElementById("showalllabel").style.visibility = "visible";
    document.getElementById("showalllabel").style.float = "right";
    document.getElementById("showonelabel").style.visibility = "hidden";
    document.getElementById("showonelabel").style.float = "none";
    loadLabelData();
}

function getUnlabelledObjects() {
    // // Create items array
//    //console.log(surfacearea)

    var userid = $("#userid").val();
    var isadmin = $("#isadmin").val();
    var workerId = $("#workerId").val();
    var assignmentId = $("#assignmentId").val();
    var hitId = $("#hitId").val();
//    console.log(userid);
//    console.log(isadmin);
    var currworker = $("#currworker").val();
    if(surfacearea.length > 0){
        //labelManager.getUnlabelledObjects(renderView.interior, renderView.totalobjects, surfacearea, currworker, isadmin, workerId, assignmentId, hitId, function(data){
        labelManager.getUnlabelledObjects( renderView.totalobjects, surfacearea, currworker, isadmin, workerId, assignmentId, hitId, function(data){
        if(data["index"] == -1) {
             alert("You have labelled all components. Click Done-Submit to submit your hit"); 
        }
        else { 
        lastunselectedIndex = data["key"];
        surfaceareaindex = data["index"];
        surfaceareaOfunselectedIndex = surfacearea[surfaceareaindex];
        surfacearea.splice(surfaceareaindex,1);
        surfacearea.push(surfaceareaOfunselectedIndex);
        removeWireFrame();
        addWireFrame([lastunselectedIndex]);
        renderView.getCameraFocustoObject(lastunselectedIndex);
        }
    });
   } else {
//      console.log("You have labelled all components. Click Done-Submit to submit your hit"); 
   }
}

function getPreviouslyLabelledObjects(){
    var userid = $("#userid").val();
    var isadmin = $("#isadmin").val();
    var workerId = $("#workerId").val();
    var assignmentId = $("#assignmentId").val();
    var hitId = $("#hitId").val();
//    console.log(userid);
//    console.log(isadmin);
//    console.log(workerId);
    var currworker = $("#currworker").val();
    labelManager.getPreviouslyLabelledObjects(currworker, isadmin, workerId, assignmentId, hitId, function(data, callback){
        var obj_label = data["data"];
        renderView.colorPreviouslyLabelledObjects(obj_label);
        for(var index in obj_label) {
            labelManager.updateLabelForIndices(userid, currmodel, [parseInt(index)], [], obj_label[index], function(data){
//                console.log(data);
            });
            surfacearealabelled += renderView.surfacearea[index];
            //if(!renderView.interior.includes(index.toString()) && !objidslabelled.includes(parseInt(index)))
            if(!objidslabelled.includes(parseInt(index)))
                objidslabelled.push(parseInt(index));
        }
	if(totalsurfacearea <= 0) {
		surfacearea = Object.keys(renderView.surfacearea).map(function(key) {
		   return [key, renderView.surfacearea[key]];
		});
	    
	       // Sort the array based on the second element
	       surfacearea.sort(function(first, second) {
		  return second[1] - first[1];
	       });

	       
	       for(var i=0; i<surfacearea.length; i++){
		    totalsurfacearea += renderView.surfacearea[i];
	       }
	}

	var complete = Math.ceil(surfacearealabelled*100.0/totalsurfacearea*1.0);
	document.getElementById('exteriorcomponents').innerHTML = String(complete)+"% complete"
        updatePercent(complete);

	if(complete >= 70) {
	    document.getElementById("rewritehit").value=1;
	    document.getElementById("bonuslabel").style.visibility="visible";
	} else {
	    document.getElementById("bonuslabel").style.visibility="hidden";
	}
    });

	labelManager.getDistinctLabels(workerId, function(data) {
		document.getElementById('distinct_labels').value = parseInt(data);
	});
}

function addWireFrame(indices) {
    if(!indices){
        //wireframeindices = [];
        return;
    }
    wireframeindices = wireframeindices.concat(indices.slice(0));
 
    for(var i=0; i < indices.length; i++){
        var obj = renderView_texture.scene.getObjectByName(renderView_texture.objs[indices[i]].name);
        
//       var geometry = new THREE.Geometry().fromBufferGeometry(obj.geometry);

//        var quickHull = new THREE.QuickHull().setFromPoints(geometry.vertices);
//        var hullvertices = quickHull.vertices;
//        console.log(hullvertices);
//      
//        var points = Array();
//        for(var j=0; j<hullvertices.length; j++){
//             points.push(hullvertices[j].point);
//        }
//
//        var meanx=0, meany=0, meanz=0;
//        for(var j=0; j < points.length; j++) {
//            meanx += points[j].x;
//            meany += points[j].y;
//            meanz += points[j].z;
//        }
//        meanx /= points.length;
//        meany /= points.length;
//        meanz /= points.length;
//
//        var newpoints = Array();
//        for(var j=0; j < points.length; j++) {
//            newpoints.push(new THREE.Vector3(points[j].x - meanx, points[j].y - meany, points[j].z - meanz));
//        }
//
//        var varx=0, vary=0, varz=0, cvarxy=0, cvarxz=0, cvaryz=0;
//        for(var j=0; j<newpoints.length; j++) {
//            varx += newpoints[j].x *newpoints[j].x;
//            vary += newpoints[j].y *newpoints[j].y;
//            varz += newpoints[j].z *newpoints[j].z;
//            cvarxy += newpoints[j].x * newpoints[j].y;
//            cvarxz += newpoints[j].x * newpoints[j].z;
//            cvaryz += newpoints[j].y * newpoints[j].z;
//        }
//        varx /= (newpoints.length-1);
//        vary /= (newpoints.length-1);
//        varz /= (newpoints.length-1);
//        cvarxy /= (newpoints.length-1);
//        cvarxz /= (newpoints.length-1);
//        cvaryz /= (newpoints.length-1);
//
//        var covmatrix = ([[varx, cvarxy, cvarxz],[cvarxy, vary, cvaryz],[cvarxz, cvaryz, varz]]);
//        console.log(covmatrix);
//
//        var eg = numeric.eig(covmatrix);
//        console.log(eg);
//
//        var eig1 = new THREE.Vector3(eg.E.x[0][0], eg.E.x[0][1], eg.E.x[0][2]);
//        eig1.normalize();
//        var eig2 = new THREE.Vector3(eg.E.x[1][0], eg.E.x[1][1], eg.E.x[1][2]);
//        eig2.normalize();
//        var eig3 = new THREE.Vector3(eg.E.x[2][0], eg.E.x[2][1], eg.E.x[2][2]);
//        eig3.normalize();
//
//        var transpoints = Array();
//        var maxx = undefined;
//        var maxy = undefined;
//        var maxz = undefined;
//        for(var j=0; j < points.length; j++) {
//            var v = points[j].clone()
//            v = new THREE.Vector3(v.dot(eig1), v.dot(eig2), v.dot(eig3));
//            if(maxx === undefined){
//                maxx = v.x;
//                minx = v.x;
//                maxy = v.y;
//                miny = v.y;
//                maxz = v.z;
//                minz = v.z;
//            }
//            else {
//                maxx = Math.max(maxx, v.x);
//                maxy = Math.max(maxy, v.y);
//                maxz = Math.max(maxz, v.z);
//                minx = Math.min(minx, v.x);
//                miny = Math.min(miny, v.y);
//                minz = Math.min(minz, v.z);
//            }
//        }
//
//        var center = new THREE.Vector3((minx+maxx)/2, (miny+maxy)/2, (minz+maxz)/2);
//        var extend = new THREE.Vector3((maxx-minx)/2, (maxy-miny)/2, (maxz-minz)/2);
//        var T = new THREE.Matrix4();
//        T.set(eig1.x, eig2.x, eig3.x, 0, eig1.y, eig2.y, eig3.y, 0, eig1.z, eig2.z, eig3.z, 0, 0, 0, 0, 1); 
//        center.applyMatrix4(T);
//
//
//        T.set(eig1.x, eig2.x, eig3.x, center.x, eig1.y, eig2.y, eig3.y, center.y, eig1.z, eig2.z, eig3.z, center.z, 0, 0, 0, 1);
//
//        var c1 = new THREE.Vector3(-extend.x, -extend.y, -extend.z);
//        var c2 = new THREE.Vector3(extend.x, -extend.y, -extend.z);
//        var c3 = new THREE.Vector3(extend.x, extend.y, -extend.z);
//        var c4 = new THREE.Vector3(-extend.x, extend.y, -extend.z);
//        var c5 = new THREE.Vector3(-extend.x, -extend.y, extend.z);
//        var c6 = new THREE.Vector3(extend.x, -extend.y, extend.z);
//        var c7 = new THREE.Vector3(extend.x, extend.y, extend.z);
//        var c8 = new THREE.Vector3(-extend.x, extend.y, extend.z);
//        
//
//        c1.applyMatrix4(T);
//        c2.applyMatrix4(T);
//        c3.applyMatrix4(T);
//        c4.applyMatrix4(T);
//        c5.applyMatrix4(T);
//        c6.applyMatrix4(T);
//        c7.applyMatrix4(T);
//        c8.applyMatrix4(T);
//
//
//        var rotx = eig1.angleTo(new THREE.Vector3(1,0,0));
//        var roty = eig2.angleTo(new THREE.Vector3(0,1,0));
//        var rotz = eig3.angleTo(new THREE.Vector3(0,0,1));

          var objc = new THREE.Vector3();
              var bb = new THREE.BoxHelper(obj);
        var rb = new THREE.LineSegments(bb.geometry, redmaterial);
            rb.geometry.computeBoundingBox();
            rb.geometry.boundingBox.getCenter(objc);

      obj.geometry.computeBoundingBox();
        var center = new THREE.Vector3();
        obj.geometry.boundingBox.getCenter(center);
        

        obj.geometry.translate(-center.x, -center.y, -center.z);

        var bbox = new THREE.Box3();
        var index = undefined;
        var minvolume = undefined;
        var degree = 0;
        var final;
        for(var j=0; j <= 360; j+=10) {
            var rad = j*Math.PI/180;
            obj.geometry.rotateZ(j*Math.PI/180);
            var b = new THREE.BoxHelper(obj);
            bbox.setFromObject(obj);
            var v = (Math.abs(bbox.max.x - bbox.min.x )*Math.abs(bbox.max.y - bbox.min.y)*Math.abs(bbox.max.z - bbox.min.z));
            if(minvolume === undefined)
            {
                minvolume = v;
                index = b.clone();
                degree = j;
                final = bbox.clone();
            } else {
                if(v < minvolume){
                    minvolume = v;
                    index = b.clone();
                    degree = j;
                    final = bbox.clone();
                }
            }
           

            obj.geometry.rotateZ(-j*Math.PI/180);
        }

        var rad = degree*Math.PI/180;
            obj.geometry.rotateZ(degree*Math.PI/180);
            var b = new THREE.BoxHelper(obj);
            
          var redmaterial = new THREE.LineBasicMaterial({color:0x00ff00, linewidth:3});
            var redbox = new THREE.LineSegments(b.geometry, redmaterial);
            var c = new THREE.Vector3();
            redbox.geometry.computeBoundingBox();
            redbox.geometry.boundingBox.getCenter(c);
            redbox.geometry.center();
        
           
            redbox.rotateY(-(degree+1)*Math.PI/180);
            redbox.position.set(objc.x,objc.y,objc.z);
            redbox.name = obj.name+"_red_wireframe";


            b = new THREE.BoxHelper(obj);
            var yellowmaterial = new THREE.LineBasicMaterial({color:0xffff00, linewidth:10});
            var yellowbox = new THREE.LineSegments(b.geometry, yellowmaterial);
            yellowbox.geometry.computeBoundingBox();
            yellowbox.geometry.boundingBox.getCenter(c);
            yellowbox.geometry.center();
        
           
            yellowbox.rotateY(-(degree+1)*Math.PI/180);
            yellowbox.position.set(objc.x,objc.y,objc.z);
            yellowbox.name = obj.name+"_yellow_wireframe";

            obj.geometry.rotateZ(-degree*Math.PI/180);
        
           renderView_texture.scene.add(redbox);
           renderView_texture.scene.add(yellowbox);
            obj.geometry.translate(center.x, center.y, center.z);

      

    }
}

function removeWireFrame(){
    for(var i=0; i < wireframeindices.length; i++){
        
        var obj = renderView_texture.scene.getObjectByName(renderView_texture.objs[wireframeindices[i]].name+"_yellow_wireframe");
        if(obj)
        {
//            //console.log("removing yellow box");
	    renderView_texture.scene.remove(obj);
        }
        var red_obj = renderView_texture.scene.getObjectByName(renderView_texture.objs[wireframeindices[i]].name+"_red_wireframe");
        if(red_obj)
        {
//            //console.log("removing red box");
	    renderView_texture.scene.remove(red_obj);
        }
    }
    wireframeindices = [];
    renderView_texture.scene.updateMatrix();
}

function incrementNumSkipsForUser() {
    var userid = $("#userid").val();
    labelManager.incrementNumSkips(userid, function(data) {
         console.log(data);
         if(parseInt(data) > 5){
             alert("You cannot skip more than 10 buildings. You have already skipped "+ data.toString()+" buildings");
         }
         if(parseInt(data) > 10) {
             window.location.href = "thankyou_skipbuilding.html";
         }
    });
}

function updatePercent(percent) {
    var userid = $("#userid").val();
    labelManager.updatePercent(userid,percent,function(data) {
//         console.log(data);
    });
}

function onMouseDown(event) {
   if(event.which === 3 || event.button === 2){
//    console.log("mouse down");
    removeWireFrame(); 
    renderView.setAnimating(false);
    renderView.onMouseDown(event);
    indices = renderView.indicesOfSelectedObjs();
    addWireFrame(indices);
    if(indices.length > 0)
        var label = labelManager.labelForMeshObjectAtIndex(currmodel, indices[0]);
        if(label)
            document.getElementById("component_label").innerHTML = "This component label :: "+label.toUpperCase(); 
        else
            document.getElementById("component_label").innerHTML = ""; 
    }
    $('#labellink').blur();
}

function onWindowResize() {
    
    var offsets_color = document.getElementById('container-color').getBoundingClientRect();
    var offsets_texture = document.getElementById('container-texture').getBoundingClientRect();
   
    renderView.frame = new Frame(offsets_color.top, offsets_color.left, offsets_color.width, offsets_color.height );
    renderView_texture.frame = new Frame(offsets_color.top , offsets_texture.left, offsets_texture.width, offsets_texture.height);
    renderView.onWindowResize();
    renderView_texture.onWindowResize();
}

function onMouseMove(event) {
//    //console.log("mouse move");
    renderView.onMouseMove(event);
}

function onMouseUp(event) {
//    //console.log("mouse up");
    renderView.onMouseUp(event);
    //renderView_texture.onMouseUp(event);
}

function onKeyDown(event) {
//    console.log(event.which);
    $('#labellink').blur();
    
    if(event.which == 13){
        $("#label_form").submit();
    } 

    if(event.which == 69)
    {
        selectParent();
    }
    if(event.which == 83)
    {
        selectChildren();
    }
    if(event.which == 73)
    {
        selectSimilar();
    }

    if(event.which == 8 || event.which == 46){
        var indices = renderView.indicesOfSelectedObjs();
        var objnames = renderView.objnameOfSelectedObjs();
        var filename = renderView.current_filename;
        var userid = $("#userid").val();
        var workerId = $("#workerId").val();

//        var exporter = new THREE.OBJExporter();
//        var result = exporter.parse(renderView.rootObj);
//        var blob = new Blob( [result], {type: 'text/plain'});
//        var link = document.createElement('a');
//        link.style.display  = 'none';
//        document.body.appendChild(link);
//
//        link.href = URL.createObjectURL(blob);
//        link.download = 'test.obj';
//        link.click();

        if(indices !== undefined){
            if (indices.length > 0) {
                var labels = labelManager.labelsForFile(filename);
                labelManager.removeLabelForIndices(userid, filename, indices, objnames, function (data) {
                    status = data["status"];
                    num_cannot_label = data["num_cannot_label"]
                    if (status != 'success') {
                        alert("Something went wrong. Could not delete the label. Error: " + status);
                    }else{
                        cannot_label -= num_cannot_label;
                        //removeUnusedLabel();
                        var surfaceareaunlabelled = 0;
                        var removed = [];
                        indices = data["indices"];
                        for(var i=0; i<indices.length; i++){
                                if(!removed.includes(indices[i].toString())){
                                    removed.push(indices[i].toString());
                                    surfaceareaunlabelled += renderView.surfacearea[indices[i]];
                                }
                        }
                        for(var i=0; i<objidslabelled.length; i++) {
                            if(indices.includes(objidslabelled[i]))
                            {
                                objidslabelled.splice(i,1);
                                i--;
                            }
                        }
                        surfacearealabelled = surfacearealabelled - surfaceareaunlabelled;
                        var complete = Math.ceil(surfacearealabelled*100.0/totalsurfacearea*1.0);
                        document.getElementById('exteriorcomponents').innerHTML = String(complete)+"% complete"
                        updatePercent(complete);

			if(complete >= 70) {
			    document.getElementById("rewritehit").value=1;
			    document.getElementById("bonuslabel").style.visibility="visible";
			} else {
			    document.getElementById("bonuslabel").style.visibility="hidden";
			}
//	                console.log(document.getElementById("rewritehit").value);
                    }
                });

            }
        }
        else if (indices.length > 0){
            var nextIndex = (indices[0] + 1) % renderView.cameraInfo.length;
            renderView.showObjectAtIndices([nextIndex], true);
        }
                labelManager.getDistinctLabels(workerId, function(data) {
                        document.getElementById('distinct_labels').value = parseInt(data);
                });
        
    }
    
    renderView.onKeyDown(event);
    document.getElementById("unlabelled").blur();
}

function onKeyUp(event) {
    renderView.onKeyUp(event);
}

