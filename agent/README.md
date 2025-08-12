# Requirements
-   Ollama must be installed locally
    Instructions to install Ollama: [https://ollama.com/download](https://ollama.com/download)
    Install using default values

-   At least 1 model needs to be pulled and ollama server must be started
    "granite-embedding:30m" model is only 63MB. The following commands will pull and run the model to start
    $ ollama run granite-embedding:30m

# Considerations
-   Because this is an "evaluation" type of exercise, the pipeline will run up to 3 different models to attempt to achieve minimum threshold configured.
    Under normal circumstances, this would be part of exploration and fine tuning at the beginning of a new pipeline to determine the best models to use.
    Once the pipeline is in production, interative improvements would be handled different based on feedback and data collection.

-   Cost of tokens has been preconfigured to a specific value for the purpose of this exercise. Under production environment, costs would be configured
    more accurately per model and specific api functions.
    
-   First Run 
    Results (latency) from the first run may be inaccurate due to initial model downloads and setup.

# Running only the pipeline

## LINUX - Execute in Active venv
$ pip install -r agent/requirements.txt
$ chmod +x agent/pipeline.py
$ ./agent/pipeline.py

## WINDOWS - Execute in Active venv
$ pip install -r agent/requirements.txt
$ python ./agent/pipeline.py

# Running entire process including result validation

## LINUX
$ ./run.sh

## WINDOWS
$ run.bat
