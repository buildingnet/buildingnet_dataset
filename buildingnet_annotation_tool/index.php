<?php
header('X-Frame-Options: ALLOWALL');
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

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

if (isset($_GET["workerId"]) && isset($_GET["assignmentId"]) && isset($_GET["hitId"])) {
	$_SESSION["mturk"] = "yes";

	$_SESSION["workerId"] = (!isset($_GET['workerId'])) ? "NA" : $_GET['workerId'];
	$_SESSION["assignmentId"] = (!isset($_GET['assignmentId'])) ? "NA" : $_GET['assignmentId'];
	$_SESSION["hitId"] = (!isset($_GET['hitId'])) ? "NA" : $_GET['hitId'];

	$server = "localhost";
	$username = "db_username";
	$password = "db_password";
	$dbname = "db_name";


	$conn = new mysqli($server, $username, $password, $dbname);
	if ($conn->connect_error) {
		die("connection failed: " . $conn->connect_error);
	}
        if((strcmp($_SESSION["workerId"], "NA") != 0) && (!empty($_SESSION["workerId"]))){
        $selectuserinfo = "SELECT * FROM `userinfo` WHERE `workerid` = '".$_SESSION["workerId"]."' AND `timespent` > 0;";
        $selectResult = $conn->query($selectuserinfo);
        $numrows = $selectResult->num_rows;
        if($numrows >= 200) {
           header('location: previousworker.html');
           exit;
        }
       }
        
       if(!isset($_GET["workerId"])) {
            header("Location: noworkerid.html");
            exit();
        }

		$check = "SELECT COUNT(1) FROM userinfo u WHERE u.workerid = '".$_SESSION["workerId"]."';";
		$run = $conn->query($check);
		$row = $run->fetch_assoc();
		$result = $row["COUNT(1)"];
	$conn->close();

}
elseif(isset($_SESSION["end_time"]) && isset($_GET["hitId"])) {
    
    session_unset();
    session_destroy();
    header("Location:  hitsubmit.html");
    exit();
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
        <style>
            td,th {
               border:1px solid #dddddd;
               padding: 8px;
             }
         </style>
</head>
<body id="main_body" >

<img id="top" src="images/top.png" alt="">
<div id="form_container">

	<h1>Labeling building parts</h1>

<?php
  if(!isset($_GET["workerId"])){
  ?>
                   <form id="consentform" method="POST">
                    </form>
  <form class="appnitro" id="emailForm"  method="post" action="labeldifferences.php">
    <div class="form_description">
      <h2>&nbsp;</h2>
            <p> Welcome again! You did a good job labeling 3D buildings before. Thus, if you wish, you can continue labeling more buildings!</p>
      <p>
        In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
        give a tag (label) to those segments e.g., window, door, wall, tower/steeple etc</p>


        <p>If you are doing the task for the first time, PLEASE WATCH THE VIDEO below to understand the task and our interface: </p>
                <!--                <iframe width="1280" height="720" src="https://www.youtube.com/embed/BsUOyHK0nKk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

                <video id="vidID_no_wid" width="100%" height="70%" controls>
            <source src="videos/intro_complete.mov" type="video/mp4">
              Your browser does not support the video tag.
        </video>
        <br/>
                                <br/>
                                <p style="text-align:center"> Watch the complete tutorial here :<a href="complete_tutorial.php" target="_blank"> link </a></p>
        <br/>
        <br/>
        <p style="font-size:15px; padding:10px; text-align:center; background-color: #dddddd;">Some <b>USEFUL</b> functionalities you <b>WANT</b> to know for faster and easier labelling: </p>
                             <table style="text-align: center; border-collapse:collapse">
          <tr>
                                    <th style="background-color: #ff8566">Select <b>SIMILAR</b> components</th>
                                    <th style="background-color: #ff8566"><b>EXPAND</b> components</th>
                                    <th style="background-color: #ff8566"><b>SHRINK</b> components</th>
                                  </tr>
                                   <tr style="height:0;">
            <td><video id="vidsimilarID" width="100%"  controls>
                      <source src="videos/similar_functionality_1min.mov" type="video/mp4" />
                     Your browser does not support the video tag.
                  </video></td>
            <td><video id="videxpandID" width="100%"  controls>
                    <source src="videos/expand2.mov" type="video/mp4">
              Your browser does not support the video tag.
            </video></td>
                  <td><video id="vidlabelID" width="100%"  controls>
                    <source src="videos/shrink3.mov" type="video/mp4">
              Your browser does not support the video tag.
            </video>
                                    <td>
                                  </tr>
                              </table>
        <br/>
        <br/>
                                <p>If you agree to take part in this study, you will be asked to interact with the interface shown in the video to label the displayed pieces of the building. The questionnaire was tested on Google Chrome, Microsoft Internet Explorer and Firefox. We do not guarantee that it will work on other browsers. The questionnaire takes about 20-30 minutes to complete (including ~12 minutes to watch the tutorial).</p>
                                <p><b>You will be rewarded with 0.50$ if you finish AT LEAST 70% of the building and use AT LEAST 3 different tags.</b><p>
                                <p><b>You will be rewarded with a bonus +0.25$(total 0.75$) if you finish AT LEAST 80% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>You will be rewarded with a bonus +0.50$(total 1$) if you finish AT LEAST 90% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>ASSIGNING RANDOM LABELS WILL RESULT IN NO REWARD</b><p>

<p style="font-size:20px; text-align:center; border-style:solid; border-color:green; border-width:10px; padding:15px; background-color:#ff8566" > You must <b> ACCEPT THE HIT </b> to continue</p>


  </form>
</div>

	<?php
  }
	else if (isset($result) && ($result<1)){
	?>
                   <form id="consentform" method="POST">
                    </form>
	<form class="appnitro" id="emailForm"  method="post" action="labeldifferences.php">
		<div class="form_description">
			<h2>&nbsp;</h2>
            <p> Welcome again! You did a good job labeling 3D buildings before. Thus, if you wish, you can continue labeling more buildings!</p>
			<p>
				In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
				give a tag (label) to those segments e.g., window, door, wall, tower/steeple etc</p>


				<p>If you are doing the task for the first time, PLEASE WATCH THE VIDEO below to understand the task and our interface: </p>
                <!--                <iframe width="1280" height="720" src="https://www.youtube.com/embed/BsUOyHK0nKk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->

                <video id="vidID" width="100%" height="70%" controls>
    				<source src="videos/intro_complete.mov" type="video/mp4">
    					Your browser does not support the video tag.
				</video>
				<br/>
                                <br/>
                                <p style="text-align:center"> Watch the complete tutorial here :<a href="complete_tutorial.php" target="_blank"> link </a></p>
				<br/>
				<br/>
				<p style="font-size:15px; padding:10px; text-align:center; background-color: #dddddd;">Some <b>USEFUL</b> functionalities you <b>WANT</b> to know for faster and easier labelling: </p>
                             <table style="text-align: center; border-collapse:collapse">
				  <tr>
                                    <th style="background-color: #ff8566">Select <b>SIMILAR</b> components</th>
                                    <th style="background-color: #ff8566"><b>EXPAND</b> components</th>
                                    <th style="background-color: #ff8566"><b>SHRINK</b> components</th>
                                  </tr>
                                   <tr style="height:0;">
				    <td><video id="vidsimilarID" width="100%"  controls>
			                <source src="videos/similar_functionality_1min.mov" type="video/mp4" />
			    	         Your browser does not support the video tag.
			            </video></td>
				    <td><video id="videxpandID" width="100%"  controls>
    				        <source src="videos/expand2.mov" type="video/mp4">
    					Your browser does not support the video tag.
				    </video></td>
			            <td><video id="vidlabelID" width="100%"  controls>
    				        <source src="videos/shrink3.mov" type="video/mp4">
    					Your browser does not support the video tag.
				    </video>
                                    <td>
                                  </tr>
                              </table>
				<br/>
				<br/>
                                <p>If you agree to take part in this study, you will be asked to interact with the interface shown in the video to label the displayed pieces of the building. The questionnaire was tested on Google Chrome, Microsoft Internet Explorer and Firefox. We do not guarantee that it will work on other browsers. The questionnaire takes about 20-30 minutes to complete (including ~12 minutes to watch the tutorial).</p>
                                <p><b>You will be rewarded with 0.50$ if you finish AT LEAST 70% of the building and use AT LEAST 3 different tags.</b><p>
                                <p><b>You will be rewarded with a bonus +0.25$(total 0.75$) if you finish AT LEAST 80% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>You will be rewarded with a bonus +0.50$(total 1$) if you finish AT LEAST 90% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>ASSIGNING RANDOM LABELS WILL RESULT IN NO REWARD</b><p>
                                <p>The NEXT button will be activated after you finish watching the 1-min main video!</p>
               

		<div class="center">
			<ul >
				<li class="buttons">
					<input id="next" class="button_text" type="submit" name="submit" disabled="disabled" value="Next" />
				</li>
			</ul>
		</div>


	</form>
</div>

	<?php
	}
	else 
	{
	?>
                    <form id="consentform" method="POST">
                    </form>
  <form class="appnitro" id="emailForm"  method="post" action="labeldifferences.php">
    <div class="form_description">
      <h2>&nbsp;</h2>
      <p> Welcome again! You did a good job labeling 3D buildings before. Thus, if you wish, you can continue labeling more buildings!</p>
      <p>
        In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
        give a tag (label) to those segments e.g., window, door, wall, tower/steeple etc</p>


        <p>If you are doing the task for the first time, PLEASE WATCH THE VIDEO below to understand the task and our interface: </p>
                <!--                <iframe width="1280" height="720" src="https://www.youtube.com/embed/BsUOyHK0nKk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe> -->
<p style="font-size:15px; padding:10px; text-align:center; background-color: #dddddd;">The NEXT button is activated this time, you can directly proceed to the next page. And the <b> SEEK </b> has been enabled in the video.</p>
                <video id="vidID_second_time" width="100%" height="70%" controls>
            <source src="videos/intro_complete.mov" type="video/mp4">
              Your browser does not support the video tag.
        </video>
        <br/>
                                <br/>
                                <p style="text-align:center"> Watch the complete tutorial here :<a href="complete_tutorial.php" target="_blank"> link </a></p>
        <br/>
        <br/>
        <p style="font-size:15px; padding:10px; text-align:center; background-color: #dddddd;">Some <b>USEFUL</b> functionalities you <b>WANT</b> to know for faster and easier labelling: </p>
                             <table style="text-align: center; border-collapse:collapse">
          <tr>
                                    <th style="background-color: #ff8566">Select <b>SIMILAR</b> components</th>
                                    <th style="background-color: #ff8566"><b>EXPAND</b> components</th>
                                    <th style="background-color: #ff8566"><b>SHRINK</b> components</th>
                                  </tr>
                                   <tr style="height:0;">
            <td><video id="vidsimilarID" width="100%"  controls>
                      <source src="videos/similar_functionality_1min.mov" type="video/mp4" />
                     Your browser does not support the video tag.
                  </video></td>
            <td><video id="videxpandID" width="100%"  controls>
                    <source src="videos/expand2.mov" type="video/mp4">
              Your browser does not support the video tag.
            </video></td>
                  <td><video id="vidlabelID" width="100%"  controls>
                    <source src="videos/shrink3.mov" type="video/mp4">
              Your browser does not support the video tag.
            </video>
                                    <td>
                                  </tr>
                              </table>
        <br/>
        <br/>
                                <p>If you agree to take part in this study, you will be asked to interact with the interface shown in the video to label the displayed pieces of the building. The questionnaire was tested on Google Chrome, Microsoft Internet Explorer and Firefox. We do not guarantee that it will work on other browsers. The questionnaire takes about 20-30 minutes to complete (including ~12 minutes to watch the tutorial).</p>
                                <p><b>You will be rewarded with 0.50$ if you finish AT LEAST 70% of the building and use AT LEAST 3 different tags.</b><p>
                                <p><b>You will be rewarded with a bonus +0.25$(total 0.75$) if you finish AT LEAST 80% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>You will be rewarded with a bonus +0.50$(total 1$) if you finish AT LEAST 90% of the building AND your labeling is verified as reasonable</b><p>
                                <p><b>ASSIGNING RANDOM LABELS WILL RESULT IN NO REWARD</b><p>
                                <p><b>The NEXT button is activated this time, you can directly proceed to the next page<b></p>
                                          <p style="font-size:15px; padding:10px; text-align:center; background-color: #dddddd;">The NEXT button is activated this time, you can directly proceed to the next page. And the <b> SEEK </b> has been enabled in the video.</p>

               

    <div class="center">
      <ul >
        <li class="buttons">
          <input id="next" class="button_text" type="submit" name="submit"  value="Next" />
        </li>
      </ul>
    </div>


  </form>
</div>

	<?php
	}
	?>
<img id="bottom" src="images/bottom.png" alt="">
</body>

<script type="text/javascript">
  		
		var video = document.getElementById('vidID');
		var timeTracking = {
                    watchedTime: 0,
                    currentTime: 0
                };
                var lastUpdated = 'currentTime';

                video.addEventListener('timeupdate', function () {
                    if (!video.seeking) {
                        if (video.currentTime > timeTracking.watchedTime) {
                            timeTracking.watchedTime = video.currentTime;
                            lastUpdated = 'watchedTime';
                        }
                        //tracking time updated  after user rewinds
                        else {
                            timeTracking.currentTime = video.currentTime;
                            lastUpdated = 'currentTime';
                        }
                    }


                });
                // prevent user from seeking
                video.addEventListener('seeking', function () {
                    // guard against infinite recursion:
                    // user seeks, seeking is fired, currentTime is modified, seeking is fired, current time is modified, ....
                    var delta = video.currentTime - timeTracking.watchedTime;
                    if (delta > 0) {
                        video.pause();
                        //play back from where the user started seeking after rewind or without rewind
                        video.currentTime = timeTracking[lastUpdated];
                        video.play();
                    }
                });
		document.getElementById('vidID').addEventListener('ended',videoEndHandler,false);
		function videoEndHandler(e) {
		document.getElementById("next").disabled = false;
		}


</script>

</html>
