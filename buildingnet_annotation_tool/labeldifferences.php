<?php
header('X-Frame-Options: ALLOWALL');
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Labelling Tool</title>
    <link rel="stylesheet" type="text/css" href="css/view.css" media="all">
    <script type="text/javascript" src="js/Index_page.js"></script>
    <script src="//code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css">
    <script type="text/javascript" charset="utf8" src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-2.0.3.js"></script>
    <script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <link rel="stylesheet" href="dist/simplePagination.css" />
</head>
<body id="main_body" >
<img id="top" src="images/top.png" alt="">
<p style="font-size:20px; padding:15px; background-color:#ff8566" >Please have a look at the following examples to be able to differentiate labels that are slightly less common.</p>

<p style="font-size:15px; ">Please scroll down to agree to the questionnaire terms. </p>
<div id="form_container">
    <table class="table table-bordered table-striped" style="width:100%;text-align:left"  border="1">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Floor</th>
                <th style="width:50%;text-align:center;font-size:25px;">Ground</th>
            </tr>  
        </thead> 
    <tbody>
    <tr> 
        <td style="font-size:16px;"> <strong><ul type="square"><li>Base of a house</li></ul><img src="js/images/floor/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/floor/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Surrounding the house excluding the floor</li></ul><img src="js/images/ground_grass/1.jpg"  width="45%" align="right" height="300" class="w3-round "><img src="js/images/ground_grass/2.jpg"  width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Parapet</th>
                <th style="width:50%;text-align:center;font-size:25px;">Balcony</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Low retaining protective wall on the edge of the roof, bridge, balcony</li></ul><img src="js/images/parapet/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/parapet/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Platform projecting from the wall, excluding the parapet surface</li></ul><img src="js/images/balcony_patio/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/balcony_patio/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Fence</th>
                <th style="width:50%;text-align:center;font-size:25px;">Railing</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Barrier for seperating houses/perimeter. Restricting access</li></ul><img src="js/images/fence/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/fence/2.jpg"   width="45%" align="left" height="300"class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Confine people to area like on a balcony, side of stairs, around patio.</li></ul><img src="js/images/railing_baluster/1.jpg"   width="45%" height="300" align="right" class="w3-round "><img src="js/images/railing_baluster/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Entrance/Gate</th>
                <th style="width:50%;text-align:center;font-size:25px;">Door</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Opening passage in fence/barrier. Opening into pathway</li></ul><img src="js/images/entrance_gate/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/entrance_gate/2.jpg"   width="45%" height="300" align="left" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Opening for indoors</li></ul><img src="js/images/door/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/door/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Awning</th>
                <th style="width:50%;text-align:center;font-size:25px;">Canopy</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  

        <td style="font-size:16px;"> <strong><ul type="square"><li>Front of building/window for shade</li><li>Needs support</li></ul><img src="js/images/awning/3.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/awning/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Self Supported</li></ul><img src="js/images/canopy_gazebo/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/canopy_gazebo/2.jpg"   width="45%" height="300" align="right" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Beam/Frame</th>
                <th style="width:50%;text-align:center;font-size:25px;">Column</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
                <td style="font-size:16px;"> <strong><ul type="square"><li>Load from slabs to columns.</li><li>Prevents bending</li></ul><img src="js/images/beam_frame/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/beam_frame/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
                <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Vertical.</li><li>Load from roof to floor.</li></ul><img src="js/images/column/1.jpg"  width="45%" align="right" height="300" class="w3-round "><img src="js/images/column/2.jpg" align="right"  width="45%" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Ceiling</th>
                <th style="width:50%;text-align:center;font-size:25px;">Roof</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Upper surface of a room (interior)</li></ul><img src="js/images/ceiling/1.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/ceiling/2.jpg"  width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Upper surface of a building (exterior)</li></ul><img src="js/images/roof/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/roof/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Dormer</th>
                <th style="width:50%;text-align:center;font-size:25px;">Roof</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Window structure on roof (including the window)</li></ul><img src="js/images/dormer/1.jpg"  width="45%" align="left" height="300" class="w3-round "><img src="js/images/dormer/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Upper surface of a building </li></ul><img src="js/images/roof/1.jpg"   width="45%" align="right" height="300"class="w3-round "><img src="js/images/roof/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>

    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Ramp</th>
                <th style="width:50%;text-align:center;font-size:25px;">Stairs</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>An inclined structure to slide on.</li></ul><img src="js/images/ramp/1.jpg"  width="45%" align="left" height="300" class="w3-round "><img src="js/images/ramp/2.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Have steps to walk on.</li></ul><img src="js/images/stairs/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/stairs/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>

    <table class="table table-bordered table-striped" style="width:100%;text-align:left">  
        <thead>  
            <tr>  
                <th style="width:50%;text-align:center;font-size:25px;">Road</th>
                <th style="width:50%;text-align:center;font-size:25px;">Corridor/Path</th>
            </tr>  
        </thead> 
    <tbody>
    <tr>  
        <td style="font-size:16px;"> <strong><ul type="square"><li>Pathway from entrance towards house/garage</li></ul><img src="js/images/road/3.jpg"   width="45%" align="left" height="300" class="w3-round "><img src="js/images/road/4.jpg"   width="45%" align="left" height="300" class="w3-round"></td>
        <td style="font-size:16px;"> <strong><ul type="square" style="padding-left:10%"><li>Narron hall with rooms leading off</li></ul><img src="js/images/corridor_path/1.jpg"   width="45%" align="right" height="300" class="w3-round "><img src="js/images/corridor_path/2.jpg"   width="45%" align="right" height="300" class="w3-round"></td>
     </tr>  
    </tbody>
    </table>
    <h1>Labeling building parts</h1>
                   <form id="consentform" method="POST">
                    </form>
    <form class="appnitro" id="emailForm"  method="post" action="labelling.php">
        <div class="form_description">
            <h2>&nbsp;</h2>
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
</html>
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
