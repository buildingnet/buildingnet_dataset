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
            $userid=$_POST["rw_userid"];
            $_SESSION["workerId"]=$workerid;
            $_SESSION["userid"]=$userid;
            $_SESSION["assignmentId"]=$_POST["rw_assignmentid"];
            $_SESSION["complete"]=false;

            // $sql = "select count(distinct(workerid)) as w_count rom buildnetlabelinfo where filename= '" . $modeldata . "';";

            $sql = "select count(distinct(workerid)) as w_count from buildnetlabelinfo where label!= 'Array' and filename='" . $model . "' and workerid in (select id from userinfo where percent >= 70);";
            if(strlen($sql) > 0) {
                $result = $conn->query($sql);
                while($row = $result->fetch_assoc()) {
                    $numcount = $row["w_count"];
                    if($completepercent >=70) {
                        if($numcount >= 5) {
		            $hits[ $model ] = 150001;
                        }
                        if($hits[$model] != 150001){
                            $hits[ $model ] = $hits[ $model] - 60000;
                        }
                        $_SESSION["complete"]=true;
                    }else {
                        $hits[$model] = $hits[$model] - 60000;
                    }
                }
            }


            $hits_file_name="data/hits.txt";

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

            $sql = "update userinfo set percent = '" . $completepercent . "' where userid = '" . $userid . "';";
            if(strlen($sql) > 0) {
                $result = $conn->query($sql);
            }
            
            $conn->close();
            header("Location: final.php");
            exit();
           ?>
