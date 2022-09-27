<?php
session_start();
header('X-Frame-Options: ALLOWALL');
$release = true;
$_SESSION["end_time"] = time();
$timeDiff = (time() - $_SESSION["start_time"]) / 60;
$timeDiff = round((float)$timeDiff, 2);
$is_complete = $_SESSION["complete"];
$invalid = ((($timeDiff < 1) && !is_complete) || ($_SESSION["label_count"] < 3));

$is_trial = isset($_SESSION["assignmentId"]) && strcmp($_SESSION["assignmentId"], "ASSIGNMENT_ID_NOT_AVAILABLE") == 0;

if (isset($_SESSION["userid"])) {
    $server = "localhost";
    $username = "username";
    $password = "password";
    $dbname = "dbname";

    $conn = new mysqli($server, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("connection failed: " . $conn->connect_error);
    }

    $sql = "UPDATE `userinfo` SET `timespent`=".$timeDiff." WHERE `id` = ".$_SESSION["userid"].";";

    //$sql = "update userinfo set percent = '" . $completepercent . "' where workerid = '" . $workerid . "';";
 
    $blacklist_file_name = "data/blacklist.txt";
    if($invalid) {
        if(!file_exists($blacklist_file_name)) {
            $blacklist_file = fopen($blacklist_file_name, "w");
            fclose($blacklist_file);
        }
         $visited = false;
        if(file_exists($blacklist_file_name)) {
            $blacklist_file = fopen($blacklist_file_name, "r");
            flock($blacklist_file, LOCK_SH);
            while(($visitor = fgets($blacklist_file)) != false) {
                 if(strcmp(trim($visitor), trim($_SESSION["workerId"])) == 0) {
                     $visited = true;
                     break;
                 }
            }
            flock($blacklist_file, LOCK_UN);
            fclose($blacklist_file);
            if(!$visited){
                $blacklist_file = fopen($blacklist_file_name, "a");
                flock($blacklist_file, LOCK_EX); //WRITER LOCK
                fwrite($blacklist_file, $_SESSION["workerId"] );
                fwrite($blacklist_file, "\n");
                flock($blacklist_file, LOCK_UN); // RELEASE LOCK
                fclose($blacklist_file);
            }          
         }
   }



  $visitor_file_name = "data/visitors.txt";
        $visited = false;
        $data = array();
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
            flock($visitor_file, LOCK_SH);
            $count = 0;
            while(($visitor = fgets($visitor_file)) != false) {
                 $data = explode("::",trim($visitor));
                if((count($data) > 0) and (strcmp(trim($data[1]), trim($_SESSION["userid"])) == 0)) {
                      $visited = true;
                      break;
                 }else {
                     $count++;
                 }
               }
            
            flock($visitor_file, LOCK_UN);
            fclose($visitor_file);
            if($visited){
                $visitor_file = fopen($visitor_file_name, "a");
                $content = file($visitor_file_name);
                flock($visitor_file, LOCK_EX); //WRITER LOCK
                $content[$count] =  $data[0]."::".$data[1]."::".$data[2]."::".$data[3]."::".time()."::".$data[5]."\n";
                file_put_contents($visitor_file_name , $content);
                flock($visitor_file, LOCK_UN); // RELEASE LOCK
                fclose($visitor_file);
            }
         }

   if(!($release)){
       $_SESSION["sandbox"] = true;
   }

    $conn->query($sql);
    $conn->close();
}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Labelling Tool</title>
	<link rel="stylesheet" type="text/css" href="css/view.css" media="all">
	<script type="text/javascript" src="js/Index_page.js"></script>

</head>
<body id="main_body" onload="document.saveForm.submit()" >

<img id="top" src="images/top.png" alt="">
<div id="form_container">

	<h1><a>Labelling</a></h1>
        <?php if(isset($_SESSION["sandbox"]) || isset($_SESSION["mturk"])) { 
		if (!$invalid && !$is_trial && is_complete && ($_SESSION["label_count"] >= 3)) { ?>
	             <form name="saveForm" class="appnitro"  method="post" action="
	             <?php
                         echo $release? "https://www.mturk.com/mturk/externalSubmit" : "https://workersandbox.mturk.com/mturk/externalSubmit";
                     ?>">
                         <INPUT TYPE="HIDDEN" id="workerId" NAME="workerId" VALUE="<?php echo($_SESSION["workerId"])?>">
                         <INPUT TYPE="HIDDEN" id="hitId" NAME="hitId" VALUE="<?php echo($_SESSION["hitId"])?>">
                         <INPUT TYPE="HIDDEN" id="assignmentId" NAME="assignmentId" VALUE="<?php echo($_SESSION["assignmentId"])?>">
                         <input id="saveForm" type="submit" id="saveForm" value="SUBMIT"/>
                        </form>
                 <?php } 
                 elseif($is_trial) {
                 ?>
                    <div class="form_description">
                    <p> This was just a preview. Results are not saved.</p>
                   </div>
                 <?php }
                elseif(!$is_complete) { 
                ?>
		    <div class="form_description">
			<p> You have labelled less than 50% of building. Sorry you cannot submit the HIT</p>
		    </div>
		<?php }
                elseif($_SESSION["label_count"] < 3) { 
                ?>
		    <div class="form_description">
			<p> You have labelled less than 3 different components. Sorry you cannot submit the HIT</p>
		    </div>
		<?php }
		else { ?>
		    <div class="form_description">
			<p> You spent way too little time.
			    looking at the shapes and selecting labels correctly..
			    Sorry but we automatically reject this task.</p>
		    </div>
            <?php } }?>

</div>
<img id="bottom" src="images/bottom.png" alt="">
<script>
 document.getElementById("saveForm").submit();
</script>
</body>
</html>
