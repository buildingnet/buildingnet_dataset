<?php
/**
 * Created by IntelliJ IDEA.
 * User: pselvaraju
 *
 *
 */

header('Content-type: application/json');
session_start();

$server = "localhost";
$username = "username";
$password = "password";
$dbname = "dbname";

$conn = new mysqli($server, $username, $password, $dbname);
if ($conn->connect_error) {
    die("connection failed: " . $conn->connect_error);
}
$labelData = Array();
$sql = "";

        $_SESSION["workerId"] = (!isset($_GET['workerId'])) ? "NA" : $_GET['workerId'];
        $_SESSION["assignmentId"] = (!isset($_GET['assignmentId'])) ? "NA" : $_GET['assignmentId'];
        $_SESSION["email"] = (!isset($_GET['email'])) ? "NA" : $_GET['email'];
        if (isset($_GET["category"])) {
                $_SESSION["category"] = $_GET["category"];
        }

 if (isset($_SESSION["email"]) && strcmp($_SESSION["email"], "NA") != 0) {
     $sql = "select * from buildnetlabelinfo inner join userinfo on buildnetlabelinfo.workerid = userinfo.id where userinfo.email='".$_SESSION["email"]."';";
 }
 if (strcmp($_SESSION["email"], "admin@arch.seg") == 0) {
         $sql = "select * from buildnetlabelinfo;";
 }
 else{
     $sql = "select * from buildnetlabelinfo inner join userinfo on buildnetlabelinfo.workerid = userinfo.id;";
 }
 if(strlen($sql) > 0) {
     $result = $conn->query($sql);
     while($row = $result->fetch_assoc()) {
         $label = $row["label"];
         $filename = $row["filename"];
         $index = (int)$row["objindex"];
         $objname = $row["objname"];
         if ((strcmp($_SESSION["email"], "admin@archseg") == 0) || isset($_SESSION["category"]) && substr($filename, 0, strlen($_SESSION["category"])) === $_SESSION["category"]) {

             if (isset($labelData[$label])) {
                 $found = false;
                 for ($i = 0; $i < count($labelData[$label]["files"]); $i++) {
                     if (strcmp($labelData[$label]["files"][$i]["filename"], $filename) == 0) {
                         $found = true;
                         $labelData[$label]["files"][$i]["indices"][] = $index;
                     }
                 }
                 if ($found === false) {
                     $obj = Array();
                     $obj["filename"] = $filename;
                     $obj["indices"] = Array($index);
                     $labelData[$label]["files"][] = $obj;
                 }
             } else {
                 $fileObj = Array();
                 $fileObj["filename"] = $filename;
                 $fileObj["indices"] = Array($index);
                 $labelObj = Array();
                 $labelObj["files"] = Array();
                 $labelObj["files"][] = $fileObj;
                 $labelData[$label] = $labelObj;
             }
         }
     }
} 

$conn->close();
echo json_encode($labelData);
?>
