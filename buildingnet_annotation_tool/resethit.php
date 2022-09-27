<?php
session_start();
          
            $model=$_POST["rw_model"];
            $hits=unserialize($_POST["rw_hits"]);
            $modeldata=unserialize($_POST["rw_modeldata"]);
            $num_modeldata=$_POST["rw_num_modeldata"];

            $hits_file_name="data/hits.txt";
            $hits[$model] = $hits[$model] - 20000;

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
           
           ?>
