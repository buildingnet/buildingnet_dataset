<?php
session_start();

	    $server = "localhost";
	    $username = "username";
	    $password = "password";
	    $dbname = "dbname";

	    $conn = new mysqli($server, $username, $password, $dbname);
	    if ($conn->connect_error) {
                die("connection failed: " . $conn->connect_error);
	    }
          
            $model=$_POST["rw_model"];
            $hits=unserialize($_POST["rw_hits"]);
            $completepercent=$_POST["rw_percent"];
            $modeldata=unserialize($_POST["rw_modeldata"]);
            $num_modeldata=$_POST["rw_num_modeldata"];
            $workerid=$_POST["rw_workerid"];
            $_SESSION["workerId"]=$workerid;
            $_SESSION["assignmentId"]=$_POST["rw_assignmentid"];
            $_SESSION["complete"]=false;

            $hits_file_name="data/admin_label_hits.txt";
            if($completepercent >= 50) {
		    $hits[ $model ] = 10001;
	            $_SESSION["complete"]=true;
            } else {
                   $hits[$model] = $hits[$model] - 20000;
            }

	    $hits_file  = fopen($hits_file_name, "r+b");
	    flock( $hits_file, LOCK_EX ); // WRITER LOCK
	    ftruncate($hits_file, 0);
	    rewind($hits_file);
	    for ($i = 0; $i < $num_modeldata; $i += 1) {
		    $num=pack("f", $hits[ $modeldata[$i] ]);
		    fwrite($hits_file, $num);
	    }
	    flock( $hits_file, LOCK_UN ); // RELEASE LOCK
	    fclose( $hits_file );

            $sql = "update userinfo set percent = '" . $completepercent . "' where workerid = '" . $workerid . "';";
            if(strlen($sql) > 0) {
                $result = $conn->query($sql);
            }

            $sql = "select count( distinct label) as total from buildnetlabelinfo b, userinfo u where u.id = b.workerid and u.workerid = '". $workerid . "';";
            $result = $conn->query($sql);
            $_SESSION['label_count'] = 0;
            if($result === FALSE)
                $_SESSION['label_count'] = $result['total'];
            
            $conn->close();
            echo ("hello");
            header("Location: noadmin.html");
            exit();
           ?>
