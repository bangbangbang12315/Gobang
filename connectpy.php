<?php
        $GLOBALS = $_POST['chessBox'];
        foreach ($GLOBALS as $val) 
        {
            $val = join(",",$val);
            $temp_array[] = $val;
        }        
        $scope =  implode(',',$temp_array);
        $output = shell_exec("python minimax.py {$scope}");
        echo($output);
?>