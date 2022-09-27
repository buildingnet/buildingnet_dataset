<?php
/**
 * Created by IntelliJ IDEA.
 * User: rajendrahn
 * Date: 02/02/16
 * Time: 5:04 PM
 */

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
session_start();
header('X-Frame-Options: ALLOWALL');
if (isset($_POST["filename"]) && isset($_POST["label"]) && isset($_POST["indices"]) && isset($_POST["userid"]) && strlen($_POST["userid"]) > 0) {

  $visitor_file_name = "data/visitors.txt";
        $visited = false;
        $data = array();
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
            flock($visitor_file, LOCK_SH);
            $count = 0;
            while(($visitor = fgets($visitor_file)) != false) {
                 $data = explode("::",trim($visitor));
                if(count($data) > 0){
                 if(strcmp(trim($data[1]), trim($_POST["userid"])) == 0) {
                      $visited = true;
                      break;
                 }else {
                     $count++;
                 }} else {
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

    $filename = $_POST["filename"];
    $newLabel = $_POST["label"];
    $indices = json_decode($_POST["indices"]);
    $objnames = json_decode($_POST["objnames"]);

	$server = "localhost";
    $username = "username";
    $password = "password";
    $dbname = "dbname";

	$conn = new mysqli($server, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("connection failed: " . $conn->connect_error);
	}

	$sql = "";
	if($newLabel == "none"){
		for($i = 0; $i < count($indices); $i++) {
			$sql .= "DELETE FROM `buildnetlabelinfo` WHERE `filename` = \"".$filename."\" and objindex = ".$indices[$i]." and workerid = ".$_POST["userid"].";";
		}
		if (strlen($sql) > 0 && $conn->multi_query($sql) === TRUE) {
                           
			//$_SESSION["label_count"] = $_SESSION["label_count"] - 1;
			    echo "success";
		} else {
			echo $conn->error;
		}
	}
	else{
		for($i = 0; $i < count($indices); $i++) {
                       
			$sql .= "DELETE FROM `buildnetlabelinfo` WHERE `filename` = \"".$filename."\" and objindex = ".$indices[$i]." and workerid = ".$_POST["userid"].";";
                        $sql .= "INSERT  INTO `buildnetlabelinfo` (`label`, `filename`, `objindex`, `objname`, `workerid`) VALUES (\"" . $newLabel . "\", \"" . $filename . "\", " . $indices[$i] . ", \"" . $objnames[$i] . "\", " . $_POST["userid"].");";
		}

		if (strlen($sql) > 0 && $conn->multi_query($sql) === TRUE) {
			$_SESSION["label_count"] = $_SESSION["label_count"] + 1;
			    echo "success";
		} else {
			if (stripos($conn->error, "PRIMARY") !== false) {
				echo "You had already labeled this object(s).";
			}
			else {
				echo $conn->error;
			}
		}
	}


	$conn->close();
}
else {
	echo ("Some essential fields are not set!");
}
