<?php
/**
 * Created by IntelliJ IDEA.
 * User: rajendrahn
 * Date: 06/06/16
 * Time: 3:21 PM
 */
header('Content-type: application/json');

$server = "localhost";
$username = "username";
$password = "password";
$dbname = "dbname";

$conn = new mysqli($server, $username, $password, $dbname);
if ($conn->connect_error) {
    die("connection failed: " . $conn->connect_error);
}

$labelData = Array();

$sql = "select count(*) as labelCount, `label` from `labelinfo` group by `label` order by `labelCount` desc;";
$result = $conn->query($sql);
while($row = $result->fetch_assoc()) {
    array_push($labelData, $row["label"]);
}

echo json_encode($labelData);
