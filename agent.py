from openai import OpenAI
from prompts.orchestrator import orchestrator_prompt
from dotenv import load_dotenv
import time
import multion
import os

load_dotenv(".env.local")

replit_email = os.getenv("REPLIT_EMAIL")
replit_password = os.getenv("REPLIT_PASSWORD")

multion_api_key = os.getenv("MULTION_API_KEY")
multion.login(use_api=True, multion_api_key=multion_api_key)

image_temp_1 = "https://cdn.sanity.io/images/bj34pdbp/migration/06f44b489e9fea1004ebd8249a0a633f52fd925f-1096x702.png?w=3840&q=75&fit=clip&auto=format"
image_temp_2 = "https://multion-client-screenshots.s3.us-east-2.amazonaws.com/0cea8653-bf81-41ac-84f2-9b08f8f2f2fa_e9209e98-8863-44e4-bc16-0ed46b1e56ca_remote_screenshot.png"


class DevOn:
    def __init__(self, editor_image, browser_image, scratchpad_image):
        self.editor_image = editor_image
        self.browser_image = browser_image
        self.scratchpad_image = scratchpad_image

        self.programmer = multion.create_session(
            {
                "input": "Log In to Repit with the email {email} and password {password}".format(
                    email=replit_email, password=replit_password
                ),
                "url": "https://replit.com/login",
                "includeScreenshot": True,
            }
        )
        while True:
            self.programmer = multion.step_session(
                self.programmer["session_id"],
                {
                    "input": "Log In to Repit with the email {email} and password {password}, and create a Python repl.".format(
                        email=replit_email, password=replit_password
                    ),
                    "url": "https://replit.com/login",
                    "includeScreenshot": True,
                },
            )
            print(self.programmer)
            if self.programmer["status"] == "DONE":
                break

        time.sleep(1)
        self.editor_image = self.programmer["screenshot"]
        self.researcher = multion.create_session(
            {
                "url": "https://www.google.com",
                "includeScreenshot": True,
            }
        )
        time.sleep(1)
        self.browser_image = self.researcher["screenshot"]
        self.notetaker = multion.create_session(
            {
                "url": "https://onlinenotepad.org/notepad",
            }
        )
        time.sleep(1)
        self.scratchpad_image = self.notetaker["screenshot"]

        self.done = True
        self.task = ""
        # self.plans = [""]
        self.plan = ""
        # self.explanations = []
        self.messages = []
        self.client = OpenAI()

    def prepare_messages(self):
        messages = [
            {"role": "user", "content": orchestrator_prompt},
            {
                "role": "user",
                "content": "The Task given to you is: {task}".format(task=self.task),
            },
            {
                "role": "user",
                "content": "The current Plan state is: {plan}".format(plan=""),
            },
        ]
        for message in self.messages:
            messages.append(message)
        return messages

    def execute_action(self, action):

        action_func = action.split(" ", 1)[0]

        if action_func == "submit":
            self.done = True
            return
        elif action_func == "update_plan":
            action_arg = action.split(" ", 1)[1]
            self.plan = action_arg
            return
        elif action_func == "programmer":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.programmer = multion.step_session(
                    self.programmer["session_id"],
                    {
                        "input": action_arg,
                        "url": "https://replit.com/login",
                        "includeScreenshot": True,
                    },
                )
                print(self.programmer)
                # time.sleep(1)
                # self.editor_image = self.programmer["screenshot"]
                if self.programmer["status"] == "DONE":
                    break
            return
        elif action_func == "researcher":
            action_arg = action.split(" ", 1)[1]
            return
        elif action_func == "notetaker":
            action_arg = action.split(" ", 1)[1]
            return
        elif action_func == "clarify":
            action_arg = action.split(" ", 1)[1]
            return

    def orchestrator(self):
        messages = self.prepare_messages()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="gpt-4-vision-preview",
            # max_tokens=200,
        )
        response = chat_completion.choices[0].message.content
        action, explanation = response.split("Explanation: ", 1)
        action = action.split("Action: ", 1)[1]

        self.execute_action(action)
        self.messages.append({"role": "assistant", "content": response})
        self.messages.append(
            {
                "role": "user",
                "content": "The current Plan state is: {plan}".format(plan=self.plan),
            }
        )

        print(self.messages)
        # temp
        # self.done = True
        return explanation

    def run(self, prompt):
        self.done = False
        self.task = prompt
        while not self.done:
            curr_response = self.orchestrator()
            yield (
                curr_response,
                self.editor_image,
                self.browser_image,
                self.scratchpad_image,
            )
