<?php
header('X-Frame-Options: ALLOWALL');
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

session_start();

$is_trial = (!isset($_SESSION["assignmentId"]) || (strcmp($_SESSION["assignmentId"], "NA") == 0) || empty($_SESSION["assignmentId"]) || !isset($_SESSION["workerId"]) || (strcmp($_SESSION["workerId"], "NA") == 0) || empty($_SESSION["workerId"]) || !isset($_SESSION["hitId"]) || (strcmp($_SESSION["hitId"], "NA") == 0) || empty($_SESSION["hitId"]));


if($is_trial) {
      $is_trial = (!isset($_POST["assignmentId"]) || (strcmp($_POST["assignmentId"], "NA") == 0) || empty($_POST["assignmentId"]) || !isset($_POST["workerId"]) || (strcmp($_POST["workerId"], "NA") == 0) || empty($_POST["workerId"]) || !isset($_POST["hitId"]) || (strcmp($_POST["hitId"], "NA") == 0) || empty($_POST["hitId"]));
      if(!$is_trial) {
          $_SESSION["workerId"]=$_POST["workerId"];
          $_SESSION["assignmentId"]=$_POST["assignmentId"];
          $_SESSION["hitId"]=$_POST["hitId"];
       }
}

$category="";

if (!$is_trial) {
    $_SESSION["start_time"] = time();
    $_SESSION["label_count"] = 0;
    $_SESSION["distinct_labels"] = 0;
    $_SESSION["percent"] = 0;
    $_SESSION["email"] = (!isset($_POST['email'])) ? "NA" : $_POST['email'];

    $server = "localhost";
    $username = "username";
    $password = "password";
    $dbname = "dbname";

    $conn = new mysqli($server, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("connection failed: " . $conn->connect_error);
    }

        $sql = "INSERT INTO `userinfo` (`workerid`, `hitid`, `assignmentid`, `email`, `timespent`, `percent`, `date`) VALUES ('" . $_SESSION["workerId"] . "','" . $_SESSION["hitId"] . "', '" . $_SESSION["assignmentId"] . "', '" . $_SESSION["email"] . "', 0, 0, NOW());";
        $conn->query($sql);
        $sql = "SELECT id FROM `userinfo` WHERE
    `workerid` = '" . $_SESSION["workerId"] . "' AND
    `hitid` = '" . $_SESSION["hitId"] . "' AND
    `assignmentid` = '" . $_SESSION["assignmentId"] . "' AND
    `email` = '" . $_SESSION["email"] . "';";
        $result = $conn->query($sql);
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $_SESSION["userid"] = $row["id"];
        }

    $conn->close();
}
elseif($is_trial){
    header("Location:noworkerid.html");
    exit();
}
else {
    $category = $_SESSION["category"];
}

// if(isset($_POST['skip'])) {
    $modeldata_file_name = "data/modeldata.txt"; //  file containing two pieces of info: model_id mesh_group_id
    $hits_file_name      = "data/hits.txt";     //  file containing number of each model datum being triggered
    $visitor_file_name  = "data/visitors.txt"; //  file recording visited workers for each data set
    $blacklist_file_name = "data/blacklist.txt"; //  file recording blacklisted workers for each data set
    $buildingskip_file_name = "data/buildingskips.txt";
    $buildingtoworkerid_file_name = "data/buildingtoworkerid.txt";
    
    
    $modeldata         = array(); // model data string
    $hits             = array(); // # hits : model data string
    $buildingskip     = array();
    $buildingtoworkerid = array();
    $percent = 0;

    $num_pages = 1; // num pages to present to the user with "real" questions
    //log_error($workerId, $assignmentId, $hitId, "test"); // debug

    // check previous visitors
//************ DO NOT DELETE. WE MIGHT BRING THIS BACK **********************
//    $visited = false;
//    if (file_exists($blacklist_file_name)) {
//            $blacklisted = false;
//            $blacklist_file = fopen($blacklist_file_name, "r");
//            flock( $blacklist_file, LOCK_SH ); // READER LOCK
//            while(($visitor = fgets($blacklist_file)) != false) {
//                    if(strcmp(trim($visitor), $_SESSION["workerId"]) == 0) {
//                            $visited = true;
//                            break;
//                    }
//            }
//            flock( $blacklist_file, LOCK_UN ); // RELEASE LOCK
//            fclose($blacklist_file);
//            if($visited)  {
//                include('previousworker.html');
//                exit();
//            }
//    }
//

        $visited = false;
        $filename_time = array();
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
            flock($visitor_file, LOCK_SH);
            while(($visitor = fgets($visitor_file)) != false) {
                 if(strlen(trim($visitor)) > 2){
                 $data = explode("::",trim($visitor));
                 $filename_time[trim($data[2])] = trim($data[3]);
                 }
            }
            flock($visitor_file, LOCK_UN);
            fclose($visitor_file);
         }

    // Load modeldata
    $modeldata_file = fopen($modeldata_file_name, "r");
    flock( $modeldata_file, LOCK_SH ); // READER LOCK
    $modeldata_id = 0;
    while (true) {
        $line = trim(fgets($modeldata_file));
        if ($line == null || strlen($line) <=1 ) break;
        $modeldata[$modeldata_id] = $line;
        $hits[$line] = 0.0;
        $buildingskip[$line]= 0.0;
        $buildingtoworkerid[$line] = array();
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


    if (!file_exists($buildingskip_file_name)) {
        $buildingskip_file = fopen($buildingskip_file_name, "wb");
        flock( $buildingskip_file, LOCK_EX ); // WRITER LOCK
        for ($modeldata_id = 0; $modeldata_id < $num_modeldata; $modeldata_id += 1) {
            $num = pack("f", 0.0);
            fwrite($buildingskip_file, $num);
        }
        flock( $buildingskip_file, LOCK_UN ); // RELEASE LOCK
        fclose( $buildingskip_file );
    }

    if (!file_exists($buildingtoworkerid_file_name)) {
        $buildingtoworkerid_file = fopen($buildingtoworkerid_file_name, "w+");
        flock( $buildingtoworkerid_file, LOCK_EX ); // WRITER LOCK
        
        $arr = [];
        for ($modeldata_id = 0; $modeldata_id < $num_modeldata; $modeldata_id += 1) {
            $arr[$modeldata[$modeldata_id]]= [];//array();
            //fwrite($buildingtoworkerid_file, json_encode($arr));
        }
        fwrite($buildingtoworkerid_file, json_encode($arr));
        flock( $buildingtoworkerid_file, LOCK_UN ); // RELEASE LOCK
        fclose( $buildingtoworkerid_file );
    }

    // Load hits data for models
    $hits_file  = fopen($hits_file_name, "r+b");
    flock( $hits_file, LOCK_EX ); // WRITER LOCK
    $data = fread($hits_file, filesize( $hits_file_name ));
    $hits_data = unpack("f*", $data); // NOTE: unpack returns associative array which starts with index 1


    // Load building skip data for models
    $buildingskip_file  = fopen($buildingskip_file_name, "r+b");
    flock( $buildingskip_file, LOCK_EX ); // WRITER LOCK
    $bdata = fread($buildingskip_file, filesize( $buildingskip_file_name ));
    $buildingskip_data = unpack("f*", $bdata); // NOTE: unpack returns associative array which starts with index 1


    // Load building skip data for models
    $buildingtoworkerid_file  = fopen($buildingtoworkerid_file_name, "r+b");
    flock( $buildingtoworkerid_file, LOCK_EX ); // WRITER LOCK
    $bdata = fread($buildingtoworkerid_file, filesize( $buildingtoworkerid_file_name ));
    $buildingtoworkerid_data = json_decode($bdata, True);// unpack("f*", $bdata); // NOTE: unpack returns associative array which starts with index 1

    print_r($buildingtoworkerid_data);
    print_r("**********");
    //print_r(json_decode($buildingtoworkerid_data, True));
    $buildingtoworkerid = $buildingtoworkerid_data;

     // create candidate lists with minimum number of hits
    for ($modeldata_id = 0; $modeldata_id < $num_modeldata; $modeldata_id += 1) {
             $hits[ $modeldata[$modeldata_id] ] = $hits_data[ $modeldata_id+1 ];
             $buildingskip[ $modeldata[$modeldata_id]] = $buildingskip_data[ $modeldata_id + 1];
             //$buildingtoworkerid[ $modeldata[$modeldata_id]] = $buildingtoworkerid_data[$modeldata[$modeldata_id]];
    }

    //print_r($buildingtoworkerid);


    if(isset($_POST["isSkipmodel"])) {
         $hits[$_POST["isSkipmodel"]] = $hits[$_POST["isSkipmodel"]] - 60000;
         $buildingskip[$_POST["isSkipmodel"]] = $buildingskip[$_POST["isSkipmodel"]] + 1;
    }
    ftruncate($buildingskip_file, 0);
    rewind($buildingskip_file);
    for ($i = 0; $i < $num_modeldata; $i += 1) {
            $num=pack("f", $buildingskip[ $modeldata[$i] ]);
            fwrite($buildingskip_file, $num);
    }
    flock( $buildingskip_file, LOCK_UN ); // RELEASE LOCK
    fclose( $buildingskip_file );

    print_r($hits);

    foreach ($hits as $key => $val) {
        if($buildingskip[$key] > 3){
            $hits[$key] = 150001;
        }
        if(($val >= 60000) &&($val < 150000)) {
           if(array_key_exists($key, $filename_time)) {
            $one = (int)$filename_time[trim($key)];
            $two = time();
            $diff = $two - $one;
            if($diff > 5) {
                $hits[$key] = $hits[$key] - 60000;
            }
          }
        }
     }

    $sorted_hits = $hits;
    foreach ($sorted_hits as $key => $val) {
        //$sorted_hits[ $key ] =  $val + mt_rand(0, 49999) / 100000;
        $sorted_hits[ $key ] =  $val + mt_rand(0, 9999) / 100000;
    }
    asort( $sorted_hits );
    $num_questions = 0;
    $questions = array();
    if($num_questions < $num_pages) {
    foreach ($sorted_hits as $key => $val) {
        if($val < 60000) {
            $questions[$num_questions]  = $key;
            $num_questions += 1;
            if ($num_questions == $num_pages) break; // V: keep all questions, will add sentinels later
        }
     }
    }
    if($num_questions <= 0) {
        include('notify.html');
    }

    // update hits data
    for ($i = 0; $i < $num_pages; $i += 1) {
            //$hits[ $questions[$i] ] = floor($hits[ $questions[$i] ]) + 0.5;
            $hits[ $questions[$i] ] = $hits[ $questions[$i] ] + 0.1;
    }


    // V: Make sure that there are enough candidates to process
    if ( ($num_questions < $num_pages) ) {
       header("Location: notify.html");
        exit();
        //echo("Sorry "It seems that there are no more available data to process at this time. Please release the HIT and try again later !");
    }

    $skipcount = -1;
    $skipvisited = false;
    if(isset($_POST["skipId"]) && $_POST["skipId"] == 1){
        if(!file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "w");
            fclose($visitor_file);
        }
        $skipcount = 0;
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
            flock($visitor_file, LOCK_SH);
            while(($visitor = fgets($visitor_file)) != false) {
                 $data = explode("::",trim($visitor));
                 if((count($data) > 0) && (strcmp(trim($data[1]), $_SESSION["userid"]) == 0) && (strcmp(trim($data[2]), $_POST["isSkipmodel"]) == 0)) {
                     $skipvisited = true;
                     break;
                 }else{
                     $skipcount++;
                 }
            }
            flock($visitor_file, LOCK_UN);
            fclose($visitor_file);
         }
    }

   // V: Shuffle the first num_pages+num_sentinel examples and put them at the end
    $shuffled_questions = $questions;
    shuffle($shuffled_questions);
    $questions = $shuffled_questions;
    $num_questions = sizeof($questions);
    $model = $questions[0];
    
    $qcount = 0;

//    print_r($buildingtoworkerid[$model]);

    $workerids = array_values($buildingtoworkerid[$model]);//json_decode(json_encode($buildingtoworkerid[$model]), True));
//    print_r($workerid_values);
//    $workerids = array(); 
//    for($i=0; $i<count($workerid_values); $i +=1)
//    {
//        #array_push($workerids, unpack("A*", $workerid_values[$i]));
//        array_push($workerids, $workerid_values[$i]);
//    }
    print_r($workerids);
    while(in_array($_SESSION["workerId"], $workerids)){
        print_r("in array");
        print_r($_SESSION["workerId"]);
        print_r($workerids);
        if($qcount < $num_questions)
        {
            $model = $questions[$qcount];
            $qcount++;
        }
        else
        {
//	    ftruncate($buildingtoworkerid_file, 0);
//	    rewind($buildingtoworkerid_file);
//	    for ($i = 0; $i < $num_modeldata; $i += 1) {
//		    $value= $buildingtoworkerid[ $modeldata[$i]];
//		    fwrite($buildingtoworkerid_file, $value);
//	    }
	    flock( $buildingtoworkerid_file, LOCK_UN ); // RELEASE LOCK
	    fclose( $buildingtoworkerid_file );
          header("Location:notify.html");
          exit();
        }
    } 



    $buildingtoworkerid[$model][] = $_SESSION["workerId"];
    ftruncate($buildingtoworkerid_file, 0);
    rewind($buildingtoworkerid_file);
    $arr = array();
    for ($i = 0; $i < $num_modeldata; $i += 1) {
        $arr[$modeldata[$i]] = $buildingtoworkerid[$modeldata[$i]];
    }
    fwrite($buildingtoworkerid_file, json_encode($arr));
    flock( $buildingtoworkerid_file, LOCK_UN ); // RELEASE LOCK
    fclose( $buildingtoworkerid_file );

    $hits[$model] = $hits[$model] + 60000;
    //print_r($hits);
    ftruncate($hits_file, 0);
    rewind($hits_file);
    for ($i = 0; $i < $num_modeldata; $i += 1) {
            $num=pack("f", $hits[ $modeldata[$i] ]);
            fwrite($hits_file, $num);
    }
    flock( $hits_file, LOCK_UN ); // RELEASE LOCK
    fclose( $hits_file );


    if($skipcount >= 0){
        if(file_exists($visitor_file_name)) {
                $visitor_file = fopen($visitor_file_name, "a");
                $content = file($visitor_file_name);
                flock($visitor_file, LOCK_EX); //WRITER LOCK
                $data = explode("::",trim($content[$skipcount]));
                $content[$skipcount] = trim($data[0])."::".$data[1]."::".$model."::".$data[3]."::".$data[4]."::0\n";
                file_put_contents($visitor_file_name , $content);
                flock($visitor_file, LOCK_UN); // RELEASE LOCK
                fclose($visitor_file);
                $skipcount = -1;
         }
   }  
   if(!file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "w");
            fclose($visitor_file);
    }
    
   if(!isset($_POST["skipId"])){
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
                $visitor_file = fopen($visitor_file_name, "a");
                flock($visitor_file, LOCK_EX); //WRITER LOCK
                fwrite($visitor_file, $_SESSION["workerId"]."::".$_SESSION["userid"]. "::" . $model . "::" . time(). "::". time()."::0\n");
                flock($visitor_file, LOCK_UN); // RELEASE LOCK
                fclose($visitor_file);
         }
      }
    
 //  echo "<form method=POST action='labelling.php'>";
//  }

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
<style>
body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}

</style>
<body class="w3-light-grey w3-content" id="main_main" style="width:100%; max-width:90vw; height:100vh">


<!-- !PAGE CONTENT! -->
<div class="w3-main" id="main" style=" left:float:left;display:inline-block; position:relative; width:100%; margin 0 auto;">

  <!-- Header -->
  <header id="portfolio" style="margin-top:10px;  position:relative">
    
    <!--<span class="w3-button w3-hide-large w3-xxlarge w3-hover-text-grey" onclick="w3_open()"><i class="fa fa-bars"></i></span> -->

    <div id="information" style="display:table; width:60%; position:relative; float:left; border:0.5px solid grey; ;padding-right: 0px;">
       <div style="float:left; width:50%; padding:0px; border:0px">
	      <ul style="list-style-type: square; padding-left:8%; margin:0px">
	      <li class="info"><b>Rotate building:</b> Left click & Drag</li>
	      <li class="info"><b>Pan:</b> Alt key + Left click & Drag</li>
	      <li class="info"><b>Zoom:</b> 's' key + Left click & Drag / Mouse wheel / Finger Swipe</li>
	      <li class="info"><b>Assign/Delete Label:</b> Right click part + enter/delete key</li>
	      </ul>
      </div>
       <div style="float:left; width:50%; padding:0px; border:0px">
	      <ul style="list-style-type: square; padding-left:5%; margin:0px">
	      <li class="info"><b>No more parts with this label:</b> 'Next&gt;&gt' button</li>
	      <li class="info"><b>Goto previous label:</b> '&lt;&ltPrevious' button</li>
	      <li class="info"><b>Select/Unselect multiple parts:</b> ctrl + right click </li>
	      </ul>
      </div>
    </div>
    <div id="single_label" class="w3-container w3-center" style=" text-align:center; display:inline-block; width:40%; position:relative">
   
   <div style=" position:relative; display:inline-block; float:right;">
      <button class="previous" id="prevbutton" style="display: inline-block; position:alsolute; bottom:0" onclick="previousFunction();">&laquo; Previous</button>
      <button class="next" id="nextbutton" style="display:inline-block;" onclick="nextFunction();">Next &raquo;</button>
      <button class="newbutton" id="showalllabel" style="display:inline-block; visibility:visible" onclick="showAllLabelFunction();">View all Labels</button>
      <button class="newbutton" style="display:inline-block; color: red; background-color: black; float:right; visibility: hidden;" name="showonelabel" id="showonelabel" onclick="showOneLabelFunction();">View one label</button>
      <div id="bonuslabel" style="position:relative; visibility:hidden; color:red;font-size:13px "><b> DO NOT FORGET to click the 'Done-Submit' button if satisfied with labelling.</b></div>
    </div>
  </header>

  <!-- View Container -->
  <div class="w3-row" id="modelcontainer" style="position:relative; position:inline-block;  max-height: 1600px; height:70vh" >
    <div class="w3-col m5 w3-blue-grey " style="display:inline-block;position:relative; width:62%; height:100vh" id="container-color" >
    <span id="exteriorcomponents" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%"></span>
    <span id=">=50% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:5%">>=50% valid: 0.25$ reward</span>
    <span id=">=70% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:8%">>=70% valid: bonus +0.25$=0.5$</span>
    <span id=">=90% complete" style="background-color:black; display:inline-block; color:white;position:absolute; left:5%; top:11%">>=90% valid: bonus +0.75$=1.0$</span>
    <?php if (strcmp($_SESSION["user"], "mturk") != 0) { ?>
    <span id="admin_exteriorcomponents" style="background-color:black; display:inline-block; color:white;position:absolute; left:25%"></span>
    <?php } ?>
    <span id="component_label" style="background-color:black;  color:yellow;position:absolute; left:20%; bottom:90%;font-size:20px;"></span>
   <div class="modal" style="text-align:center; position:absolute; left:35%; top:1%">
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
      <div id="labeling" style=" padding-top:0.01%; padding-right:5%">
        <form action="update_label_json.php" id="label_form" style="float:right; display:inline-block;position:relative;">
                <input type="hidden" name="userid" id="userid" value="<?php echo $is_trial ? "" :$_SESSION["userid"];?>">
                <input type="hidden" name="isadmin" id="isadmin" value=false>
             <input type="hidden" id="workerId" name="workerId" value=<?php echo($_SESSION["workerId"])?>>
             <input type="hidden" id="assignmentId" name="assignmentId" value=<?php echo($_SESSION["assignmentId"])?>>
             <input type="hidden" id="hitId" name="hitId" value=<?php echo($_SESSION["hitId"]) ?>>
             <input type="hidden" id="distinct_labels" name="distinct_labels" value=0>
             <input type="hidden" id="issubmit" name="issubmit" value=0>
             <button id="submit" class="newbutton" style="display:inline-block; padding:11px;visibility: visible;" onclick="validateSubmit()">Done - Submit task</button>
        </form>
        <form action="rewritehit.php" method="post" id="rewritehitform" name="rewritehitform">
             <input type="hidden" id="rewritehit" name="rewritehit" value=0>
             <input type="hidden" id="rw_model" name="rw_model" value=<?php echo($model)?>>
             <input type="hidden" id="rw_workerid" name="rw_workerid" value=<?php echo($_SESSION["workerId"])?>>
             <input type="hidden" id="rw_assignmentid" name="rw_assignmentid" value=<?php echo($_SESSION["assignmentId"])?>>
             <input type="hidden" id="rw_percent" name="rw_percent" value=0 >
             <input type="hidden" id="rw_num_modeldata" name="rw_num_modeldata" value=<?php echo($num_modeldata)?>>
             <input type="hidden" id="rw_modeldata" name="rw_modeldata" value=<?php echo(serialize($modeldata))?>>
             <input type="hidden" id="rw_hits" name="rw_hits" value=<?php echo(serialize($hits)); ?>>
         </form>
        <div style="display:inline-block; padding:30px; float:right; position:relative"></div>
        
        <form onsubmit="return validateSkip()" method="post" action="labelling.php">
             <input type="submit" class="newbutton" style="position:relative; display:inline-block; float: right; visibility: visible; padding:10px" id="skip" value="skip this building" name="skip">
             <input type="hidden" id="workerId" name="workerId" value=<?php echo($_SESSION["workerId"])?>>
             <input type="hidden" id="isSkipmodel" name="isSkipmodel" value=<?php echo($model)?>>
             <input type="hidden" id="assignmentId" name="assignmentId" value=<?php echo($_SESSION["assignmentId"])?>>
             <input type="hidden" id="hitId" name="hitId" value=<?php echo($_SESSION["hitId"]) ?>>
             <input type="hidden" id="skipId" name="skipId" value=1>
        </form>
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
   document.getElementById("rw_percent").value = complete;
   var label_count = document.getElementById("distinct_labels").value;
   document.getElementById("issubmit").value = 1;
   if(parseInt(label_count) < 3) {
       alert("Warning! You must use at least 3 different tags and label at least 70% of the building to submit the task");
   }
   else if(parseInt(complete) < 70){
      alert("Warning!! You must label at least 70% of the building to be able to submit the task");
   }
   else{
document.getElementById("rewritehitform").submit();
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
<script src="libs/js/loaders/TextureLoader.js"></script>
<script src="libs/js/loaders/TGALoader.js"></script>
<script src="libs/js/loaders/ImageLoader.js"></script>
<script src="libs/js/loaders/DataTextureLoader.js"></script>
<script src="libs/js/loaders/BufferGeometryLoader.js"></script>
<script src="libs/js/loaders/CompressedTextureLoader.js"></script>
<script src="libs/js/loaders/CubeTextureLoader.js"></script>
<script src="libs/js/loaders/ImageBitmapLoader.js"></script>
<script src="libs/js/loaders/Loader.js"></script>
<script src="libs/js/loaders/MaterialLoader.js"></script>
<script src="libs/js/loaders/DDSLoader.js"></script>
<script src="libs/js/tween.min.js"></script>
<script src="libs/js/controls/TrackballControls.js"></script>
<script src="libs/js/exporters/OBJExporter.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/numeral.js/2.0.6/numeral.min.js"></script>
<script src="js/View.js"></script>
<script src="js/main.js"></script>
<script src="js/colorbrewer.js"></script>
<script src="js/category.js"></script>
</html>
