# Audio transcribe

A lightweight Python / Streamlit application that let's you easily set up a service to transcribe audio files.
You need a subscription at [assemblyai](https://www.assemblyai.com) to use their transcription API.
It comes with a free 50$ budget for starting and uses ~15 cent for a 20 minute interview to subscribe.
Since this is for private fun, the site has a simple one password for all users as login.


## Install
- create an environment
- activate it
- pip install streamlit assemblyai python-dotenv


## Configure
You need to set the two passwords, one for the AssemblyAI API and one for your user login to the page.
Too do so you need to create a file called `.env`.
There two variables have to be set. An example is given in `.env.example`.


## Run locally
`streamlit run app.py`


## Run in `docker`

- **Build:** `docker build -t transcribe .`
- **Run:** `docker run -p 8502:8502 --user $(id -u):$(id -g) transcribe`
- **Access:** `http://localhost:8502`