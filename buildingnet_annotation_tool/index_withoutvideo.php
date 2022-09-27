<?php
header('X-Frame-Options: ALLOWALL');

function genRandomString() {
	$length = 15;
	$characters = "0123456789abcdefghijklmnopqrstuvwxyz";
	$string = "";
	for ($p = 0; $p < $length; $p++) {
		$string .= $characters[mt_rand(0, strlen($characters)-1)];
	}
	return $string;
}

mt_srand(crc32(microtime()));

session_start();

$_SESSION["start_time"] = time(); 
if (isset($_GET["user"])) {
	$_SESSION["user"] = $_GET["user"];
	if (isset($_GET["category"])) {
		$_SESSION["category"] = $_GET["category"];
	}
}
else {
	$_SESSION["user"] = "mturk";
}


if (isset($_GET["assignmentId"])) {
	$_SESSION["mturk"] = "yes";

	$_SESSION["workerId"] = (!isset($_GET['workerId'])) ? "NA" : $_GET['workerId'];
	$_SESSION["assignmentId"] = (!isset($_GET['assignmentId'])) ? "NA" : $_GET['assignmentId'];
	$_SESSION["hitId"] = (!isset($_GET['hitId'])) ? "NA" : $_GET['hitId'];

	$server = "localhost";
    $username = "username";
    $password = "password";
    $dbname = "dbname";

	$conn = new mysqli($server, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("connection failed: " . $conn->connect_error);
	}

	$duplicate = false;
	$selectSQL = "SELECT * FROM `workerinfo` WHERE `workerid` = '".$_SESSION["workerId"]."';";
	$selectResult = $conn->query($selectSQL);
	if ($selectResult->num_rows != 0) {
		$duplicate = true;
	}
	$conn->close();

	//TODO: remove invalidating the duplicate. This is here for testing
	$duplicate = false;
}

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Labelling Tool</title>
	<link rel="stylesheet" type="text/css" href="css/view.css" media="all">
	<script type="text/javascript" src="js/Index_page.js"></script>
	<script src="//code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
</head>
<body id="main_body" >

<img id="top" src="images/top.png" alt="">
<div id="form_container">

	<h1>Labeling building parts</h1>
	<form class="appnitro" id="emailForm"  method="post" action="labelling.php">
		<div class="form_description">
			<h2>&nbsp;</h2>
			<p>
				In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
				give a tag (label) to those segments e.g., window, door, tower, pinnacle etc</p>
			<?php if (strcmp($_SESSION["user"], "expert") == 0) { ?>
				<p>Below is a video demonstrating the use of our interface for labeling building components.</p>
				<video width="60%" controls>
					<source src="videos/video_tutorial_1080HD.mp4" type="video/mp4">
					Your browser does not support HTML5 video.
				</video>
				<br/>
				<br/>
				<p>Here is also a summary of instructions:</p>
			<p>
				On the left side of our interface, you will find a list of buildings. Please try to label parts from <b>20 buildings</b>,
				whichever you prefer most.
				Feel free to explore the listed buildings and skip the ones that are too hard to label.</p>
			<?php } ?>
			<p>Clicking one of the buildings will load a model in the main display area. In the main display area, you can
				rotate the 3D model by dragging, zoom by scrolling, and pan by dragging with Shift key pressed.
				You can right click to select a segment. Once a segment is selected, it will be shown in white color.
				You need to type the tag (label)
				for the <strong>selected</strong> segment in the text-box at the bottom of interface,
				and then <strong>click the 'Enter label' button.</strong> </p>
			<p>To help you in the process, here is some additional functionality:</p>

			<ol>
				<li>You can select multiple identical components by Ctrl + right click so that you label them altogether at the same time. </li>
				<li>You can add a component to currently selected components by Alt + right click. </li>
				<li>You can remove a component from currently selected component by Alt + right click. </li>
				<li>Components with the same label will have the same color.</li>
				<li>All the currently labeled parts for a building will be listed in a sub-list on the left of the
					interface under the building name you are currently working on. </li>
				<li>All part labels you entered for all buildings will appear on the right of the interface.
					You can label a component directly by clicking one of the listed part labels instead of re-typing
					its text label.</li>
			</ol>


			<p> <strong>Please label as many parts as possible (preferably all of them per building).</strong> </p>

			<p>Your participation is voluntary and you have the right to withdraw
				your consent or discontinue participation at any time. By clicking the
				button below, you give your consent for your anonymous responses to be
				used in a scientific study and in scientific publications. Your
				individual privacy will be completely maintained in all published and
				written data resulting from the study. </p>
			<?php if (strcmp($_SESSION["user"], "mturk") == 0) { ?>
			<p> At the end of the questionnaire, we perform automatic tests to determine if you attempted to
				cheat the task or were too inconsistent in your answers.
				In such cases, your work will not be useful for us and will not be accepted.</p>
			<?php } ?>
			<p> To start, click next.</p>
			<?php if (strcmp($_SESSION["user"], "expert") == 0) { ?>
			<p>Please enter your email so that we can send you an Amazon  gift card for your participation.</p>
				<label for="email">Email: </label>
				<input type="text" name="email" id = "email"/>
			<?php } ?>
		</div>

		<div class="center">
			<ul >
				<li class="buttons">
					<input id="saveForm" class="button_text" type="submit" name="submit" value="Next" />
				</li>
			</ul>
		</div>


	</form>
</div>
<img id="bottom" src="images/bottom.png" alt="">
</body>

<?php if (strcmp($_SESSION["user"], "expert") == 0) { ?>
<script>
	function isEmail(email) {
		var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
		return regex.test(email);
	}

	$("#emailForm").submit(function (event) {
		var text  = $("#email").val();
		if (text.length == 0 || !isEmail(text)) {
			alert("Please enter the email address.");
			event.preventDefault();
		}
	});
</script>

<?php } ?>
</html>
