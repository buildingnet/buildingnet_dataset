<?php
/**
 * Created by IntelliJ IDEA.
 * User: rajendrahn
 * Date: 11/04/16
 * Time: 1:53 PM
 */

session_start();

header('Content-type: application/json');
$string = file_get_contents("./js/objects.json");
$obj_json = json_decode($string);
srand((double) microtime() * 1000000);


if (isset($_SESSION["user"])) {
    if (strcmp($_SESSION["user"], "admin") == 0) {
        echo $string;
    }
    elseif (strcmp($_SESSION["user"], "expert") == 0) {

        if (isset($_SESSION["category"])) {
            $query = $_SESSION["category"];
            $selected = array();
            for ($i = count($obj_json); $i >= 0; $i--) {
                $obj = (array)$obj_json[$i];
                if (substr($obj["filename"], 0, strlen($query)) === $query) {
                    $selected[] = $obj_json[$i];
                    #echo(json_decode($obj_json[$i], true));
                }
            }
            echo json_encode($selected);
        }
        else {
            echo json_encode($obj_json);
        }
    }
    elseif (strcmp($_SESSION["user"], "mturk") == 0) {
        $chosen = array();
        $chosen[] = $obj_json[rand(0, count($obj_json) - 1)];
        echo json_encode($chosen);
    }
    else {
        echo "[]";
    }
}
else {
    echo "[]";
}
