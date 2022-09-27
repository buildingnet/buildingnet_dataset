
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
<div id="form_container" style="margin:20px; padding:20px">

	<h1>Labeling building parts</h1>
		<div class="form_description">
			<h2>&nbsp;</h2>
			<p>
				In this questionnaire, you will be shown 3D  models of buildings. Your task is to select parts on the exterior of the 3D buildings and
				give a tag (label) to those segments e.g., window, door, wall, tower/steeple etc</p>
				<p>Below is a video demonstrating the use of our interface for labeling building components.</p>
                                <iframe width="1280" height="720" src="https://www.youtube.com/embed/JPwO-J4erbI" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
				<br/>
				<br/>

                                <p><b>PARTS OF INTERFACE</b></p>
                                <br/>
                                <p><b>Main Display:</b></p>
                                <p>The main display area has two windows.</p>
                                <p> Left – Shows the 3D building with parts color coded. This is the MAIN window where all the interactions happen.</p>
                                <p> Right window – Same building with texture information for easier identification of parts. This window does NOT provide any interaction of any kind. It reflects the motion of the building on the left window.</p>
                                <br/>

                                <p><b>Labeling instructions (Top Left):</b></p>
                                <p>This table shows the commonly used functionalities and instructions which will help in labeling the parts, such as how to select or un-select parts, how to select all similar parts etc.,</p>
                                <p><b>Part Label (Top Right):</b></p>
                                <p>The header shows what is the label the currently selected part will be tagged to.</p>
                                <p><b> Skip/Submit (Bottom Right):</b></p>
                                 <p>Buttons to skip the building if the building does not have many meaningful parts or submit your labeling when you think you are done.</p>

                                <br/>

                               <p><b>INSTRUCTION/FUNCTIONALITIES FOR LABELING:</b></p>
                                <p>Please wait for a few seconds until the building is loaded in the window area. If for any reason thebuilding is not displayed, refresh your browser.</p>
                                <p>In the Left window display, you can try to.
                                <ol>
                                 <li><b>ROTATE</b> the view of the building by clicking and holding the LEFT MOUSE button and dragging it.</li>
                                 <li><b>MOVE/PAN</b> the view by pressing and holding ‘ALT’ key followed by clicking the LEFT MOUSE button and dragging it.</li>
                                 <li><b>ZOOM IN/OUT</b> the view by scrolling the MOUSE WHEEL. In case of mouse pads, use two FINGER SWIPES.  You can do the same with keyboard shortcuts by pressing 's' key and clicking and holding the LEFT MOUSE button and dragging it.</li>
                                </ol>
                                <br/>

                                 <p><b>HOW TO LABEL PARTS?</b></p>
                                 <p>Your main task is to label parts of the building. All the buildings are pre-segmented into small parts. All the different building parts are shown with different shades of green in our interface.
Your task is to group these parts into meaningful parts that carry a label.</p>
                                 <p><b>To label:</b>On opening the interface we will show you on the HEADER the label for which you need to select the part. For e.g., if the HEADER shows as ‘DOOR’, then you start by selecting a part whichyou think corresponds to a DOOR by right clicking on that part. If the part is selected, then it becomes ‘WHITE’.  Followed by it if you press ‘ENTER’ key, then that particular part will be labeled as ‘DOOR’ and will be color coded accordingly.</p>
                                  <p>In many cases, several parts can be described by the same part label. So you can either repeat the action mentioned above, or press and hold ‘CONTROL’ key and right click on parts and once all the parts which you think belong to a particular label is selected, press the ‘ENTER’ key. This will tag all the parts selected to that particular label.</p>
<p><b>To delete a label:</b> Select part(s) for which you want to remove the label. Press ‘DELETE’ key.</p>
                            <p>Once you think you have identified all the parts for that particular label on the header, click the ‘NEXT’ button. This will show the another label on the header for which you need to repeat the same actions.</p>
                                 <br/>

                               <p><b>Useful buttons/functionalities:</b></p>
                                <ol>
                                     <li><b>SIMILAR(‘i’):</b> Selecting SIMILAR PARTS by pressing the ‘SIMILAR (‘i’) ‘ button or pressing key ‘i’ in the keyboard, to select parts which look similar to the part(s) selected.</li>
                                     <li><b>EXPAND(‘e’): </b>Selecting siblings for the part(s) selected by pressing the ‘EXPAND (‘e’)’ button in the left window display. Since the buildings are organized by tree structure, depending upon the way it is structured, this button click will select all the siblings of the current selection.</li>
                                     <li><b>SHRINK(‘s’): </b> Unselecting siblings for the part(s) selected by pressing the ‘SHRINK (‘s’)’ button in the left window display. This will unselect all the siblings which were selected by pressing expand key. </li>
                                    <li><b>UNSELECT:</b> After selecting parts for labeling, if you want to unselect a part(s) press and hold ‘CTRL’ key and click on the part.
                                </ol>

                                 <p>Once you have circled through all the available labels, then the interface will show you all the labels as a list. In case you have missed labeling a part you can select the part and select the label from the list and tag it.</p>
                                 <p><b>FIND UNLABELED PARTS: </b> If you could not identify a part just by looking at the interface but the components labeled has not reached > 95 %, then you can try clicking the <b>‘Find Unlabeled Parts’</b> button in the left display. This will show you the part which has not been labeled before by highlighting it in ‘red’ color.By selecting a label from the list and pressing ENTER, this particular part will be tagged with the label selected.</p>

<p>All the key combinations are shown on the top left of your interface as a reminder. At any point, you can click ‘Help! video tutorial & instruction’ to check our interface functionality to revisit this page.</p> 
<p>Finally, there might be buildings whose pre-segmented components are not ideal, as in this example, where multiple semantic parts belong to the same component. Unfortunately, such buildings cannot be reliably labeled. There might be several buildings with this kind of problem. Ifyou encounter such buildings, feel free to SKIP the buildings by pressing ‘Skip this building’ button, which will automatically load a new building for you. Ideally, we would like you to label allparts, or almost (95%) all parts correctly.Once you are done labeling click on the ‘DONE-SUBMIT’ button.</p>

		</div>
</div>
<img id="bottom" src="images/bottom.png" alt="">
</body>

</html>
