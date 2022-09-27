<!DOCTYPE HTML>
<html>
<head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
     <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Oswald">
     <link rel="stylesheet" href="https://cdnjs.cloudfare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
     <style>
          p{
             font-size:100%;
           }
          img {
            border-radius: 10px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);
            padding: 5px;
            margin: 10px;
           }
           body {
             font-family: "Times New Roman", "Georgia", "Serif";
           }
           h1,h2,h3,h4,h5,h6 {
             font-family: "Playfair Display";
             letter-spacing: 5px;
           }
      </style>
</head>

<?php
    $label = $_GET['label'];
?>
<div class="w3 content" style="width:100" id="links">
    <?php
        $view = array();
        for($t = 1; $t<=4; $t=$t+1) {
            $view[] = "js/images/" . $label . "/" . $t . ".jpg";
        }
    ?>
   <h1 style="text-align:center"> <?php echo $label ?> </h1>
    <div class="w3-row w3-padding-20">
        <table style="width:100%; text-align:center">
           <tr>
             <td>
                <img src="<?php echo($view[0])?>" class="w3-round" style="width:400px; height:400px">
                <img src="<?php echo($view[1])?>" class="w3-round" style="width:400px; height:400px">
             </td>
		<?php
		    $label = $_GET['label'];
		    echo $label;
		?>
             <td>
                <img src="<?php echo($view[2])?>" class="w3-round" style="width:400px; height:400px">
                <img src="<?php echo($view[3])?>" class="w3-round" style="width:400px; height:400px">

    </div>
</div>
