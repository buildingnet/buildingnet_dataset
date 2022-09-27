<?php
$non_file_lines = file('files/filenotavail.txt');
$file_lines = file('files/batch/yesfile5000.txt');
?>

<!DOCTYPE html>
<html>
<head>
    <script src="//code.jquery.com/jquery-latest.min.js" type="text/javascript"></script>
<script src="libs/three.js"></script>
<script src="libs/three.min.js"></script> 
<script src="libs/js/loaders/ColladaLoader.js"></script>
<script src="libs/jszip.min.js"></script>
<script src="libs/jszip-utils.min.js"></script>
<script src="js/hierarchy.js"></script>
    <script src="js/hierarchy.js"></script>
        <script>
            loadJsonFromPHP(<?php echo json_encode($non_file_lines) ?>, <?php echo json_encode($file_lines) ?>, 'yesfile5000');
        </script>
</head>
<body>



</body>
</html>



</html> 
