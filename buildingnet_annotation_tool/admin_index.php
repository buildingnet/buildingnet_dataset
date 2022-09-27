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
                   <form id="consentform" method="POST">
                    </form>
	<form class="appnitro" id="emailForm"  method="post" action="admin_labelling.php">
		<div class="form_description">
			<h2>&nbsp;</h2>
			<p>
				In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
				give a tag (label) to those segments e.g., window, door, wall, tower/steeple etc</p>
				<p>If you are doing the task for the first time, PLEASE WATCH THE VIDEO below to understand the task and our interface: </p>
                                <iframe width="1280" height="720" src="https://www.youtube.com/embed/BsUOyHK0nKk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
				<br/>
				<br/>
                                <p>If you agree to take part in this study, you will be asked to interact with the interface shown in the video to label the displayed pieces of the building. The questionnaire was tested on Google Chrome, Microsoft Internet Explorer and Firefox. We do not guarantee that it will work on other browsers. The questionnaire takes about 20-30 minutes to complete (including ~12 minutes to watch the tutorial).</p>
                         <p>You may not directly benefit from this research; however, we hope that your participation in the study may promote computer graphics research.</p>
                        <p> We believe there are no known risks associated with this research study; however, as with any online related activity the risk of a breach of confidentiality is always possible. To the best of our ability your answers in this study will remain confidential. We will minimize any risks by storing only your answers to the questions, and not any metadata that can reveal your identity.</p>
                        <p> Your participation in this study is completely voluntary and you can withdraw at any time. You are free to skip a building to label by selecting the choice "skip building". </p>
          <br/>
          <p> By clicking “I agree to participate” below you are indicating that you are at least 18 years old, have read and understood this consent form and agree to participate in this research study.  If you choose to participate,  click "Start Questionnaire".</p>

                <tr>
               <td colspan=3>
               <div id="consent" onchange="consentFunction()">
                   <input type="radio" style="margin:0px 5px 40px 10px" id="agree" name="consent" value="agree">I agree to participate </input>
                   <input type="radio" style="margin:0px 5px 10px 40px" id="notagree" name="consent" value="notagree">I do not wish to participate </input>
               </div>
               </td>
               </tr>

		<div class="center">
			<ul >
				<li class="buttons">
					<input id="startQ" hidden=true class="button_text" type="submit" name="submit" value="Start Questionnaire" />
				</li>
			</ul>
		</div>


	</form>
</div>
<img id="bottom" src="images/bottom.png" alt="">
</body>

<script type="text/javascript">
  
        function consentFunction() {
	    if(document.getElementById("agree").checked) {
               document.getElementById("startQ").hidden = false;
            }
            else {
                document.getElementById("startQ").hidden = true;
		var form = document.getElementById("consentform");
		form.action = "notagree.php";
		form.submit();
            }
        }

</script>

</html>
