<!DOCTYPE HTML>
<html>
<head>
    <title>Buildings User Study</title>

    <noscript>
        <meta http-equiv="refresh" content="0; URL=noscript.html">
    </noscript>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href='buildnet.css' rel='stylesheet'/>  
<link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Oswald">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
 <link href="styles/pretty-checkbox.min.css" rel="stylesheet"/>

  <style>
    p {
      font-size: 100%;
    }
    span {
      display: inline-block;
      margin: 0px 0px;
    }
        img {
    
    border-radius: 10px;
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
    padding: 5px;
    margin: 10px;
}

body {font-family: "Times New Roman", Georgia, Serif;}
h1,h2,h3,h4,h5,h6 {
    font-family: "Playfair Display";
    letter-spacing: 5px;
}


.w3-row-padding img {margin-bottom: 12px}
/* Set the width of the sidebar to 120px */
.w3-sidebar {width: 120px;background: #222;}
/* Add a left margin to the "page content" that matches the width of the sidebar (120px) */
#main {margin-left: 120px}
#/* Remove margins from "page content" on small screens */
#@media only screen and (max-width: 600px) {#main {margin-left: 0}}

  </style>
</head>

<body class="w3-white">
<?php require_once 'styles/Mobile-Detect/Mobile_Detect.php';
      $detect = new Mobile_Detect;
      $device_type = ($detect->isMobile() ? ($detect->isTablet()? 'tablet' : 'phone') : 'desktop');

?>
<?php
    $file_array = file('data/datainfo/categories.txt');
  
    $cat = array();
    if($file_array) {
        foreach($file_array as $line)
      $cat[] = $line;
    }

    $check = "checked";
    $dis = 'disabled';

    $file_type = file('data/datainfo/inputtype.txt');
    $type = $file_type[0];

    $file_indexdata = file('indexdata/indexdata.txt');
    $indexdata = array();
    if($file_indexdata) {
         foreach($file_indexdata as $line)
             $indexdata[] = $line;
    }

   $file_indexdescription = file('indexdata/indexdescription.txt');
   $description = array();
   if($file_indexdescription) {
       foreach($file_indexdescription as $line)
           $description[] = $line;
   }

   $file_checks = file('indexdata/indexcat.txt');
   $check = array();
   if($file_checks) {
       foreach($file_checks as $line) {
           $check[] = $line;
       }
   }
    
?>
    <?php
        error_reporting(E_ALL);
        ini_set('display_errors', '1');
    

        function genRandomString() {
            $length = 15;
            $characters = "0123456789abcdefghijklmnopqrstuvwxyz";
            $string = "";
            for ($p = 0; $p < $length; $p++) {
                $string .= $characters[mt_rand(0, strlen($characters)-1)];
            }
            return $string;
        }
    
        function sanitize($string = '') {
            $string = str_replace("#", "%23", $string);
            $string = str_replace("_", "%5F", $string);
            $string = str_replace("-", "%2D", $string);
            return $string;
        }   

    ?>

         

  <div style="height:auto; width:100%; margin: 0 auto;" id="exdiv">
    
  <div class="w3-padding-large w3-white" style="padding:10px 0 0 0 ">
    <center style="padding:0 0 0 0">

    <!-- Header -->
    <header class="w3-display-container w3-content w3-wide" style="max-width:1600px;min-width:500px" id="home">
      <div class="w3-display-center w3-padding-large w3-opacity">
        <h1 class="w3-xxlarge">Examples</h1>
      </div>
    </header>


    <table style="width:80%;text-align:justified">
        <tbody>
        <tr>
            <td>
              <p style="font-size:18px">You are being invited to participate in a research study titled “3D Building Model Categorization”. This study is being done by Evangelos Kalogerakis from the University of Massachusetts Amherst. You were selected to participate in this study because you accepted the corresponding Amazon MTurk HIT.
                </p>
                <p style="font-size:18px">The purpose of this research study is to ask participants to categorize 3D models of buildings. If you agree to take part in this study, you will be asked to complete an online questionnaire.  Specifically, the questionnaire will show you four views of a rendered 3D building model, and display a question asking you to classify it into one or more categories (e.g., residential, commercial, religious building etc).
 You will see a total of<b><?php echo($num_questions)?></b> different questions and 3D models. After answering a question, click the button "NEXT". After pressing the &quot;"DONE!"&quot; button in the last question, your questionnaire will be automatically submitted. You may do the questionnaire multiple times if you want. The questionnaire was tested on Google Chrome, Microsoft Internet Explorer and Firefox. We do not guarantee that it will work on other browsers. The questionnaire takes about 5 minutes to complete.</p>
                <p style="font-size:18px">Here are some example questions and expected answers: </p>
            </td>
        </tr>
    </tbody></table>
    </center>


    <?php for($ex=0; $ex < 9; $ex = $ex+1) { ?>
    <div class="w3-content" style="width:100" id="ex<?php echo($ex+1)?>">
        <?php
            $view = array();
            for($t = 1; $t<=4; $t = $t+1) {
                $view[] = "indexdata/" . $t . "/" . $indexdata[$ex] . "_" . $t ."00000.jpg";
            }
        ?>
     
      <div class="w3-row w3-padding-20" >
         <?php if($detect->isMobile() or $detect->isTablet()): ?> 
    <table style="width:100%;text-align:center"><tr><td>
     <img src="<?php echo(sanitize($view[0]).'?'.time());?>" class="w3-round" style="max-width:100%; max-height:100%;">
     <img src="<?php echo(sanitize($view[1]).'?'.time());?>" class="w3-round " style="max-width:100%;max-height:100%;">
    </td><td>
     <img src="<?php echo(sanitize($view[2]).'?'.time());?>" class="w3-round" style="max-width:100%; max-height:100%;">
     <img src="<?php echo(sanitize($view[3]).'?'.time());?>" class="w3-round" style="max-width:100%; max-height:100%;">
    </td></tr>
    </table>
        <?php else : ?>
        <div class="w3-col m8 w3-padding-large w3-hide-small">
    <table style="width:100%;text-align:center"><tr><td>
     <img src="<?php echo(sanitize($view[0]).'?'.time());?>" class="w3-round " style="max-width:100%; max-height:100%;">
     <img src="<?php echo(sanitize($view[1]).'?'.time());?>" class="w3-round " style="max-width:100%;max-height:100%;">
    </td><td>
     <img src="<?php echo(sanitize($view[2]).'?'.time());?>" class="w3-round" style="max-width:100%; max-height:100%;">
     <img src="<?php echo(sanitize($view[3]).'?'.time());?>" class="w3-round" style="max-width:100%; max-height:100%;">
    </td></tr>
    </table>
        </div>
       <?php endif ?>
       


        <div class="w3-col m4 w3-padding-small">
          <h2 class="w3-center">Example Question <?php echo($ex+1)?></h2><br>

                <div style="background-color: white">
                    <?php $c = explode(",",$check[$ex]); 
                        $cc = array();
                        for($j=0; $j < count($c); $j=$j+1) { $cc[] = trim($c[$j]);}
                        for($i=0; $i<count($cat); $i = $i+1) {?> 
                           
                           <div class="pretty p-svg p-curve" style="margin:10px">
                            <input type=<?php echo($type)?> id="checkbox<?php echo($ex) ?>" name="checkbox<?php echo($ex) ?>" <?php if(in_array(trim($cat[$i]),$cc))  echo("checked"); ?> disabled="disabled" >
        <div class="state p-success">
         <svg class="svg svg-icon" viewBox="0 0 20 20">
          <path d="M7.629,14.566c0.125,0.125,0.291,0.188,0.456,0.188c0.164,0,0.329-0.062,0.456-0.188l8.219-8.221c0.252-0.252,0.252-0.659,0-0.911c-0.252-0.252-0.659-0.252-0.911,0l-7.764,7.763L4.152,9.267c-0.252-0.251-0.66-0.251-0.911,0c-0.252,0.252-0.252,0.66,0,0.911L7.629,14.566z" style="stroke: white;fill:white;"></path>
         </svg>
                 
                                 <label for="<?php echo($ex)?>-opt"><?php echo($cat[$i])?></label>
                                </div>
                           </div>
                          <br>
                    <?php } ?>
                 </div>
                 <center><p style="font-size:18px; color:#FF7F50" align="justify"><?php echo($description[$ex]) ?></p></center> 
                 </div>

        </div>
       </div>
       </hr>
      <?php } ?>

    
  
  <script type="text/javascript">
    document.getElementById("exdiv").style.maxWidth = (window.innerWidth-100)+'px' ;
                <?php for($i=0; $i < count($cat); $i++) {?>
            document.getElementById("ex<?php echo($i+1)?>").style.maxWidth = (window.innerWidth-100)+'px' ;
                <?php } ?>
                

  </script>

</div>
</div>
</div>

</body>
</html>
