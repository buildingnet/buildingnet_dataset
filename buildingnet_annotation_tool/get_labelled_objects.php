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

$objindexData =  Array();
$model = $_POST['modelname'];
$getlabel = $_POST['getlabel'];
$currworker = $_POST['currworker'];
$isadmin = $_POST["isadmin"];
$workerId = $_POST["workerId"];
$assignmentId = $_POST["assignmentId"];
$hitId = $_POST["hitId"];



if($getlabel == "1"){
    if (isset($_POST["isadmin"]) && $isadmin && isset($_POST["currworker"])) {
      $sql = "select b.objindex,b.label from buildnetlabelinfo b, userinfo u where b.workerid = u.id and u.workerid='".$currworker."' and u.workerid != '' and u.workerid != 'NA' and b.workerid != '' and b.workerid != 'NA' and b.filename='".$model."'";
    }
    else {
      $sql = "select b.objindex,b.label from buildnetlabelinfo b, userinfo u where b.workerid = u.id and u.workerid='".$_POST["workerId"]."' and u.assignmentid='".$_POST["assignmentId"]."' and u.hitid='".$_POST["hitId"]."' and b.filename='".$model."' ";
    }
      $result = $conn->query($sql);
     
      while($row = $result->fetch_assoc()) {
         $index = (int)$row["objindex"];
         $label = $row["label"];
         $objindexData[$index] = $label;
     }
 }
else {
    if (isset($_POST["isadmin"]) && $isadmin && isset($_POST['currworker'])) {
      $sql = "select b.objindex from buildnetlabelinfo b, userinfo u where b.workerid = u.id and u.workerid='".$currworker."' and b.workerid != '' and b.workerid != 'NA' and b.filename='".$model."'";
    } else {
      $sql = "select b.objindex from buildnetlabelinfo b, userinfo u where b.workerid = u.id and u.workerid='".$_POST["workerId"]."' and u.assignmentid='".$_POST["assignmentId"]."' and u.hitid='".$_POST["hitId"]."' and b.filename='".$model."' ";
    }
      $result = $conn->query($sql);
      while($row = $result->fetch_assoc()) {
         $index = (int)$row["objindex"];
         $objindexData[] = $index;
     }

 }


//if (isset($_SESSION["email"]) && strcmp($_SESSION["email"], "NA") != 0) {
//     $sql = "select objindex from buildnetlabelinfo inner join userinfo on buildnetlabelinfo.workerid = userinfo.id where userinfo.email='".$_SESSION["email"]." and buildnetlabelinfo.filename='".$model."'";
//
//     if (strcmp($_SESSION["email"], "admin@arch.seg") == 0) {
//          $sql = "select objindex from buildnetlabelinfo where buildnetlabelinfo.filename='".$model."'";
//     }
//     $result = $conn->query($sql);
//     while($row = $result->fetch_assoc()) {
//         $index = (int)$row["objindex"];
//         $objindexData[] = $index;
//     }
//
//     //$objindexData[] = "1";
// } 

$conn->close();

echo json_encode($objindexData);
//echo json_encode($sql. " " .$objindexData);
//echo json_encode($sql);;
//echo json_encode($_SESSION["workerId"]);
