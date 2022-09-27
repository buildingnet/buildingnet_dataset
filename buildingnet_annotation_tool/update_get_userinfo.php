<?php
/**
 * Created by IntelliJ IDEA.
 * User: pselvaraju
 *
 *
 */

header('Content-type: application/json');

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
session_start();

$server = "localhost";
$username = "username";
$password = "password";
$dbname = "dbname";


$conn = new mysqli($server, $username, $password, $dbname);
if ($conn->connect_error) {
    die("connection failed: " . $conn->connect_error);
}
$numskip = 0;
$sql = "";
$final = "";

        $visitor_file_name = "data/visitors.txt";
        $visited = false;
        if(file_exists($visitor_file_name)) {
            $visitor_file = fopen($visitor_file_name, "r");
            flock($visitor_file, LOCK_SH);
            $count = 0;
            while(($visitor = fgets($visitor_file)) != false) {
                 $data = explode("::",trim($visitor));
                 if((count($data)>0) and (strcmp(trim($data[1]), $_POST["userid"]) == 0)) {
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
                $content[$count] = trim($data[0])."::".$data[1]."::".$data[2]."::".$data[3]."::".$data[4]."::".$_POST["percent"]."\n";
                file_put_contents($visitor_file_name , $content);
                flock($visitor_file, LOCK_UN); // RELEASE LOCK
                fclose($visitor_file);
            }

         }


 if(isset($_POST["userid"]) && isset($_POST["percent"])){      
         
     $sql = "update userinfo set percent=".$_POST["percent"]." where id='".$_POST["userid"]."';";
     if(strlen($sql) > 0) {
         $result = $conn->query($sql);
         if($result === FALSE)
             $final = "There is some issue with updating the result";
         else
             $final = "success";
     }
  }
 elseif(isset($_POST["userid"]) && isset($_POST["isnumskip"])){      
     echo json_encode(Array('data' => $_POST["isnumskip"]));
     
     $sql = "select numskip from userinfo where id = '".$_POST["userid"]."';";
     if(strlen($sql) > 0) {
         $result = $conn->query($sql);
         while($row = $result->fetch_assoc()) {
             $numskip = $row["numskip"];
             $numskip = $numskip +1 ;
             $updatesql = "update userinfo set numskip=".$numskip." where id='".$_POST["userid"]."';";
             if($conn->query($updatesql) === FALSE)
                 $numskip = $numskip -1;
        }     
     }
  }

$conn->close();
if(isset($_POST["isnumskip"]))
    echo json_encode($numskip);
elseif(isset($_POST["percent"]))
    echo json_encode($final);
?>
