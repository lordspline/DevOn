# DevOn

What if you tried to do what Devin does, but using MultiOn's agents?

We use 3 separate MultiOn Agents, one each for programming, researching and notetaking.

Their activities are orchestrated and supervised by an overarching GPT-4V

Setup:

- Create a .env.local and set the following env variables:
  - OPENAI_API_KEY
  - MULTION_API_KEY
  - REPLIT_EMAIL (if using the remote API)
  - REPLIT_PASSWORD (if using the remote API)
- ```pip install -r requirements.txt```
- If you want to use the local API (need to have the chrome extension installed and API enabled for this): ```bash start_local.sh```
- If you want to use the remote API: ```bash start_remote.sh```

Barebones Demo:



https://github.com/lordspline/DevOn/assets/74811063/6de8ba85-3f43-415b-8fd9-eff6b2ed29c5

