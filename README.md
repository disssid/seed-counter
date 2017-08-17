# Seed Counter

1. Updated program seedCount15Aug2017wheatTest2.py for optimal seed removal

2. Updated the program seedCount15Aug2017wheatTest2.py to accept command line parameters if any, else will run with default parameters in the program. The order of the command line parameters is as follows
  
    ```python seedCount15Aug2017wheatTest2.py areaL areaH seedType flowRate```

3. added two shell scripts run-areaH and run-areaL for running all areaH and areaL possibilities on each seed type. The scipts must be given executable privileges and can be run as follows,
    
    a. to generate results for varying **areaL** values use the **run-areaL.sh**, in which the areaH is defaulted to 8000
      ``` ./run-areaL.sh```
    b. to generate results for varying **areaH** values use the **run-areaH.sh**, in which the areaL is defaulted to 200
      ``` ./run-areaH.sh```

#### Sample Run
         ~/workspace/seed-counter/src$ ./run-areaL.sh 
          Executing python programs for seed type sesame-seeds
          Progress : ################################################
          Execution done
          Executing python programs for seed type wheat
          Progress : #########################
          Execution done
          Executing python programs for seed type popcorn
          Progress : ##################
          Execution done
          Executing python programs for seed type white-soya-beans
          Progress : ###################
          Execution done
          Executing python programs for seed type red-seeds
          Progress : ##################
          Execution done
          Executing python programs for seed type brown-seeds
          Progress : ###############################################
          Execution done
          Executing python programs for seed type corn
          Progress : #######################
          Execution done

   Individual log files are generated in the ```./logs/``` directory with areaH and areaL in separate sub directories.
 
   A full report consisting of number of seeds and average area is generated in the src folder itself.
 
