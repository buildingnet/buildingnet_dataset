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
if (isset($_POST["workerId"])) {
	$server = "localhost";
	$username = "username";
	$password = "password";
	$dbname = "dbname";

	$conn = new mysqli($server, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("connection failed: " . $conn->connect_error);
	}

            $sql = "";
            $sql = "SELECT count( distinct label) as total from buildnetlabelinfo b, userinfo u where u.id = b.workerid and u.workerid = '". $_POST["workerId"] . "';";
            $result = $conn->query($sql);
            $total = $result->fetch_assoc();
            $conn->close();
            echo($total['total']);
          
}
else {
	echo ("Some essential fields are not set!");
}
