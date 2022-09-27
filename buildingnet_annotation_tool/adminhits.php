<?php
header('X-Frame-Options: ALLOWALL');

session_start();

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);    

    $adminusername = "adminusername";
    $adminpassword = "adminpassword";

    $server = "localhost";
    $username = "username";
    $password = "password";
    $dbname = "dbname";
$category="";

if ((isset($_POST["adminusername"])  && strcmp($_POST["adminusername"], $adminusername) == 0 &&
    isset($_POST["adminpassword"])   && strcmp($_POST["adminpassword"], $adminpassword) == 0) ||
    (isset($_GET["adminusername"]) && strcmp($_GET["adminusername"], $adminusername) == 0 && 
    isset($_GET["adminpassword"])   && strcmp($_GET["adminpassword"], $adminpassword) == 0)  || 
    (isset($_POST["isadmin"]) && $_POST["isadmin"]) || 
    (isset($_GET["isadmin"]) && $_GET['isadmin'])) {

      $limit = 10;
      if (isset($_GET["page"])) { $page  = $_GET["page"]; } 
      elseif (isset($_POST["page"])) { $page  = $_POST["page"]; } 
      else { $page=1; }; 
      $start_from = ($page-1) * $limit;  


    $conn = new mysqli($server, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("connection failed: " . $conn->connect_error);
    }

    //$sql = "SELECT distinct filename FROM buildnetlabelinfo where (workerid IS NOT NULL and workerid != '' and strcmp(workerid, 'NA') != 0 )";

    $currworkers = array();
    $currpercent = array();
    $workers = array();
    $percent = array();
    $buildings = array();
    //$sql = "SELECT distinct u.workerid,u.percent,b.filename FROM buildnetlabelinfo b , userinfo u where (u.percent >=90 and b.workerid=u.id and u.workerid != '' and u.workerid != 'NA') order by u.percent desc ,u.workerid desc";   
    $sql = "SELECT distinct u.workerid,u.percent,b.filename FROM buildnetlabelinfo b , userinfo u where (u.percent >=70 and u.workerid='<workerid>' and u.id = b.workerid)";   
    //echo($sql);
    $result = $conn->query($sql);
    $labeldata = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()){
           $labeldata[] = $row["filename"];
           $workers[] = $row["workerid"];
           $percent[] = $row["percent"];
           $buildings[] = $row["filename"];
         // echo $row["filename"]. ' ' .$row["percent"]. ' ' .$row["workerid"];
         // echo "<br>";

        }
    }
    if(isset($_POST["model"])){$model=$_POST["model"];}
    elseif(isset($_GET["model"])){$model=$_GET["model"];}
    else {
        $model = $labeldata[0];
    }  
    $sql = "SELECT distinct u.workerid,u.percent FROM userinfo u, buildnetlabelinfo b where u.percent >=90  and u.id=b.workerid and u.workerid != '' and u.workerid != 'NA' and b.filename='" . $model . "'";  
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
  while($row = $result->fetch_assoc()){
     $currworkers[] = $row["workerid"];
           $currpercent[] = $row["percent"];
        //echo $row["percent"]. ' ' .$row["workerid"];
        //echo "<br>";
  }
   }
  $conn->close();
   
  array_multisort($currpercent,SORT_DESC ,$currworkers); 
   $currworkerno = 0;
   if(isset($_POST["currworkerno"])) {
      $currworkerno=$_POST["currworkerno"];
      if(isset($_POST["isprevious"])){
          if($currworkerno < 0)
              $currworkerno = 0;
          else
              $currworkerno--;
      }
      else if(isset($_POST["isnext"])){
          if($currworkerno >= sizeof($currworkers))
                $currworkerno = sizeof($currworkers)-1;
          else
                $currworkerno++;
      }
   }   
 $modeldata_file_name = "data/modeldata.txt"; //  file containing two pieces of info: model_id mesh_group_id
    $hits_file_name      = "data/admin_hits.txt";     //  file containing number of each model datum being triggered
    $original_hits_file_name      = "data/hits.txt";     //  file containing number of each model datum being triggered
    if (!file_exists($hits_file_name)) {
        $hits_file = fopen($hits_file_name, "wb");
        fclose( $hits_file );
    }
    if(!copy($original_hits_file_name, $hits_file_name)) {
        echo("failed to copy");
    }
    
    $modeldata         = array(); // model data string
    $hits             = array(); // # hits : model data string

    $num_pages = 1; // num pages to present to the user with "real" questions
    //log_error($workerId, $assignmentId, $hitId, "test"); // debug


    // Load modeldata
    $modeldata_file = fopen($modeldata_file_name, "r");
    flock( $modeldata_file, LOCK_SH ); // READER LOCK
    $modeldata_id = 0;
    while (true) {
        $line = trim(fgets($modeldata_file));
        if ($line == null || strlen($line) <=1 ) break;
        $modeldata[$modeldata_id] = $line;
        $hits[$line] = 0.0;
        $modeldata_id += 1;
    }
    flock( $modeldata_file, LOCK_UN ); // RELEASE LOCK
    fclose($modeldata_file);
    $num_modeldata = sizeof($modeldata);
   // Write initial hits data for shapes if the file does not exist
    if (!file_exists($hits_file_name)) {
        $hits_file = fopen($hits_file_name, "wb");
        flock( $hits_file, LOCK_EX ); // WRITER LOCK
        for ($modeldata_id = 0; $modeldata_id < $num_modeldata; $modeldata_id += 1) {
            $num = pack("f", 0.0);
            fwrite($hits_file, $num);
        }
        flock( $hits_file, LOCK_UN ); // RELEASE LOCK
        fclose( $hits_file );
    }

    // Load hits data for models
    $hits_file  = fopen($hits_file_name, "r+b");
    flock( $hits_file, LOCK_EX ); // WRITER LOCK
    $data = fread($hits_file, filesize( $hits_file_name ));
    $hits_data = unpack("f*", $data); // NOTE: unpack returns associative array which starts with index 1
    if ( sizeof($hits_data) != $num_modeldata ) {
                    log_error($workerId, $assignmentId, $hitId,
                            "Internal error: list of files inconsistent with hit data".
                            strval(sizeof($hits_data))."!=".strval($num_modeldata)."\n");
    }

        // create candidate lists with minimum number of hits
    for ($modeldata_id = 0; $modeldata_id < $num_modeldata; $modeldata_id += 1) {
             $hits[ $modeldata[$modeldata_id] ] = $hits_data[ $modeldata_id+1 ];
    }
    //print_r($hits);
    flock( $hits_file, LOCK_UN ); // RELEASE LOCK
    fclose( $hits_file );
}
else {
    header("Location: noadmin.html");
    exit();
}

?>

<!DOCTYPE html>
<html>
<title>3D Building Labelling</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
<link rel="stylesheet" href="css/newstyles.css">
<link rel="stylesheet" href="css/dialog.css">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css">
<script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-2.0.3.js"></script>
<script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
<link rel="stylesheet" href="dist/simplePagination.css" />
<script src="dist/jquery.simplePagination.js"></script>
<style>
body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}

</style>
<body class="w3-light-grey w3-content" id="main_main" style="width:100%; max-width:90vw">


<!-- !PAGE CONTENT! -->
<div class="w3-main" id="main" style=" left:float:left;display:inline-block; position:relative; width:100%; margin 0 auto;">

  <!-- Header -->
  <header id="portfolio" style="margin-top:10px;  position:relative">
    
    <!--<span class="w3-button w3-hide-large w3-xxlarge w3-hover-text-grey" onclick="w3_open()"><i class="fa fa-bars"></i></span> -->
    <div id="information" style="display:table; width:50%; position:relative; float:left; border:0.5px solid grey; padding-right: 0px;">
       <div style="float:left; width:50%; padding:0px; border:0px">
        <ul style="list-style-type: square; padding-left:8%">
        <li class="info"><b>Rotate building:</b> Left click & Drag</li>
        <li class="info"><b>Pan:</b> Alt key + Left click & Drag</li>
        <li class="info"><b>Zoom:</b> 's' key + Left click & Drag / Mouse wheel / Finger swipe</li>
        <li class="info"><b>Assign Label:</b> Right click part + enter key</li>
        <li class="info"><b>Delete Label:</b> Right click part + delete key</li>
        </ul>
      </div>
       <div style="float:left; width:50%; padding:0px; border:0px">
        <ul style="list-style-type: square; padding-left:5%">
        <li class="info"><b>No more parts with this label:</b> 'Next&gt;&gt' button</li>
        <li class="info"><b>Goto previous labels:</b> '&lt;&ltPrevious' button</li>
        <li class="info"><b>View all labels:</b> 'View all Labels' button </li>
        <li class="info"><b>Select/Unselect multiple parts:</b> ctrl + right click </li>
        </ul>
      </div>
    </div>
    <div id="single_label" class="w3-container w3-center" style=" text-align:center; display:inline-block; width:45%; position:relative">
    
   
   <div style=" position:relative; display:inline-block; float:right;">
      <button class="previous" id="prevbutton" style="display: inline-block; position:alsolute; bottom:0" onclick="previousFunction();">&laquo; Previous</button>
      <button class="next" id="nextbutton" style="display:inline-block;" onclick="nextFunction();">Next &raquo;</button>
      <button class="newbutton" id="showalllabel" style="display:inline-block; float:right" onclick="showAllLabelFunction();">View all Labels</button>
      <button class="newbutton" style="display:inline-block; color: red; background-color: black; visibility: hidden;" name="showonelabel" id="showonelabel" onclick="showOneLabelFunction();">View one label</button>
    </div>
  </header>
  
  <!-- View Container -->
  <div class="w3-row" id="modelcontainer" style="position:relative; position:inline-block;  max-height: 1600px; height:70vh" >
    <div class="w3-blue-grey" style="display:inline-block; position:relative; width:20%; ">
     <ul>
      <?php for($i = $start_from; $i< ($start_from + $limit); $i++) { ?>
          <li>
   <form method="post" action="adminhits.php"><input type="submit" class="button" style="font-size:10px; color:blue ;position:relative; display:inline-block;" value="<?php echo($labeldata[$i]) ?>"/>
            <input type="hidden" name="model" value=<?php echo($labeldata[$i])?>>
            <input type="hidden" name="isadmin" value=1>
            <input type="hidden" name="page" value=<?php echo($page)?>>

    </form>
          </li>

      <?php } ?>
     </ul>
    </div>
   <p><?php echo($model) ?> </p>
   <p><?php print_r($currpercent) ?> </p>
   <p><?php print_r($currworkers) ?> </p>
   <p><?php print_r($currpercent[$currworkerno]) ?> </p>
   <p><?php print_r($currworkers[$currworkerno]) ?> </p>
   <form method="post" action="adminhits.php"><input type="submit" class="button" style="position:relative; display:inline-block;" value="previous">
             <input type="hidden" name="currworkerno" value=<?php echo($currworkerno) ?> >
             <input type="hidden" name="isadmin" value=1>
             <input type="hidden" name="model" value=<?php echo($model)?>>
             <input type="hidden" name="page" value=<?php echo($page)?>>
             <input type="hidden" name="isprevious" value=true>
    </form>
   <form method="post" action="adminhits.php"><input type="submit" class="button" style="position:relative; display:inline-block;" value="next">
             <input type="hidden" name="currworkerno" value=<?php echo($currworkerno) ?> >
             <input type="hidden" name="isadmin" value=1>
             <input type="hidden" name="model" value=<?php echo($model)?>>
             <input type="hidden" name="page" value=<?php echo($page)?>>
             <input type="hidden" name="isnext" value=true>
    </form>
                <input type="hidden" name="userid" id="userid" value="<?php echo $is_trial ? "" :$_SESSION["userid"];?>">
                <input type="hidden" name="isadmin" id="isadmin" value=true>
                <input type="$currper" name="currper" id="currper" value=<?php echo($currpercent[$currworkerno])?>>
                <input type="currworker" name="currworker" id="currworker" value=<?php echo($currworkers[$currworkerno]) ?>>
                <input type="hidden" name="page" value=<?php echo($page)?>>


    <div class="w3-col m5 w3-blue-grey " style="display:inline-block;position:relative; width:62%; height:100vh" id="container-color" >
    <span id="exteriorcomponents" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%"></span>
    <span id=">=50% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:5%">>=50% complete : Bonus</span>
    <span id=">=70% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:8%">>=70% complete : Bonus</span>
    <span id=">=90% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:11%">>=90% complete : Bonus</span>
    <span id=">=95% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:14%">>=95% complete : Bonus</span>
    <!--<?php if (strcmp($_SESSION["user"], "mturk") != 0) { ?>
    <span id="admin_exteriorcomponents" style="background-color:black; display:inline-block; color:white;position:absolute; left:25%"></span>
    <?php } ?> --> 
    <span id="component_label" style="background-color:black;  color:yellow;position:absolute; left:20%; bottom:90%;font-size:20px;"></span>
   <div class="modal" style="text-align:center; position:absolute; left:35%;  ">
          <button class="newbutton" style="display:inline-block;" name="parent" id="parent" onclick="selectParent();">Expand ('e')</button>
          <button class="newbutton" style="display:inline-block;" name="children" id="children" onclick="selectChildren();">Shrink ('s')</button>
          <button class="newbutton" style="display:inline-block;" name="similar" id="similar" onclick="selectSimilar();">Find Similar ('i')</button>
          <div style="padding: 2%; display: inline-block;"></div>
          <button class="newbutton" style="display:inline-block; color: red; background-color: black; visibility: hidden;" name="unlabelled" id="unlabelled" onclick="getUnlabelledObjects();">Find unlabeled parts</button>
          <button class="newbutton" style="display:inline-block;float:right" name="reset" id="reset" onclick="resetView();">Reset view</button>
    </div>
    </div>

    <div class="w3-col m2" id="labels_list" style="position:relative; display:inline-block; width: 2%;">
        <ul class="w3-ul w3-border w3-center w3-white w3-hover-opacity-off">
        </ul>
    </div>
 

    <div class="w3-col m5 w3-blue-grey " style="width:36%; height:75vh" id="container-texture">  
    </div>
    
    <div style="width:36%; float:right; border-style:groove">
      <div id="labeling" style=" padding-top:2%; padding-right:5%">

                    <button id="submit" class="newbutton" style="display:inline-block; padding:11px;visibility: visible;" onclick="validateSubmit()">Done - Submit task</button>
        <form action="rewritehit.php" method="post" id="rewritehitform" name="rewritehitform">
             <input type="hidden" id="rewritehit" name="rewritehit" value=0>
             <input type="hidden" id="model" name="model" value=<?php echo($model)?>>
             <input type="hidden" id="num_modeldata" name="num_modeldata" value=<?php echo($num_modeldata)?>>
             <input type="hidden" id="modeldata" name="modeldata" value=<?php echo(serialize($modeldata))?>>
             <input type="hidden" id="hits" name="hits" value=<?php echo(serialize($hits)); ?>>
         </form>
        <div style="display:inline-block; padding:30px; float:right; position:relative"></div>
        
        <form onsubmit="return validateSkip()" method="post" action="labelling.php"><input type="submit" class="newbutton" style="position:relative; display:inline-block; float: right; visibility: visible; padding:10px" id="skip" value="skip this building" name="skip"/></form>
  </div>
    <div style="display:inline-block; text-align:center; width:100%"><a href="index_help.php" style="color:blue; display:block; position:relative" target="_blank" >Help! see tutorial video and instructions</a></div>
    </div>
    <div id="loading-overlay" >
      <div id="loading-bar">
         <span id="progress"></span>
      </div>
    </div>
   
    <INPUT TYPE="HIDDEN" NAME="model" id="model" VALUE="<?php echo($model)?>"> 
  </div>

  <!-- Footer -->
  <!--<footer class="w3-container w3-padding-12 w3-dark-grey">-->
  <footer class="w3-container w3-padding-12">
<div id="dialogoverlay"></div>
<div id="dialogbox">
  <div>
    <div id="dialogboxhead"></div>
    <div id="dialogboxbody"></div>
    <div id="dialogboxfoot"></div>
  </div>
</div>
        <div style="display:inline-block; padding-bottom:30px; float:right; position:relative"></div>
  </footer>
<!-- End page content -->
</div>

<div id="loading" style="display: none"></div>
<div id="category" style="display:none" value="<?php echo $category ?>"></div>
</body>
<script>
<!-- Script to open and close sidebar -->
function w3_open() {
    document.getElementById("mySidebar").style.display = "block";
    document.getElementById("myOverlay").style.display = "block";
}
 
function w3_close() {
    document.getElementById("mySidebar").style.display = "none";
    document.getElementById("myOverlay").style.display = "none";
}

function myFunction() {
      document.getElementById("myDropdown").classList.toggle("show");
}

function validateSubmit() {
   var complete = 0;
   var percent = document.getElementById("exteriorcomponents").innerHTML;
   complete = parseInt(percent.split("%")[0]);  
   if(complete >=95){
      console.log(complete);
      document.getElementById("rewritehitform").submit();
  }
  else{
    location.href = 'final.php'; 
  }
}

function validateSkip() {
     if(confirm("Are you sure you want to skip labelling this building?")){
        incrementNumSkipsForUser();
        return true;
     } else {
        return false;
     }
}

function issue_warning(count) {
     alert("Warning! You have labelled "+ count.toString()+ " as cannot label")
}
function blurlabellink() {
    document.getElementById("labellink").blur();
}

</script>
<script src="//code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
<script src="libs/three.min.js"></script> 
<script src="js/LabelsManager.js"></script>
<script src="libs/js/loaders/ColladaLoader.js"></script>
<script src="libs/js/loaders/DDSLoader.js"></script>
<script src="libs/js/tween.min.js"></script>
<script src="libs/js/controls/TrackballControls.js"></script>
<script src="libs/js/exporters/OBJExporter.js"></script>
<script src="js/View.js"></script>
<script src="js/main.js"></script>
<script src="js/colorbrewer.js"></script>
<script src="js/category.js"></script>
<script src="libs/dialog.js"></script>
</html>

<?php
$num_labeldata=sizeof($labeldata);
$total_pages = ceil($num_labeldata / $limit);
$pageLink = "<nav><ul class='pagination'>";  
for ($j=1; $j<=$total_pages; $j++) {
             $firstmodel = ($j-1)*$limit;  
             $pageLink .= "<li><a href='adminhits.php?isadmin=1&adminusername=<adminusername>&adminpassword=<password>&model=$labeldata[$firstmodel]&page=".$j."'>"." ".$j."</a></li>";  
};  
echo $pageLink . "</ul></nav>"; 
?>
</div>
</body>
</html>
<script type="text/javascript">
$(document).ready(function(){
$('.pagination').pagination({
                    items: <?php echo $totalhits;?>,
                    itemsOnPage: <?php echo $limit;?>,
                    cssStyle: 'light-theme',
                    currentPage : <?php echo $page;?>,
                    hrefTextPrefix : 'adminhits.php?page='
                });
                });
</script>
