from openai import OpenAI
from prompts.orchestrator import orchestrator_prompt
from prompts.programmer import programmer_notes
from prompts.notetaker import notetaker_notes
from dotenv import load_dotenv
import time
import multion
import os

load_dotenv(".env.local")

replit_email = os.getenv("REPLIT_EMAIL")
replit_password = os.getenv("REPLIT_PASSWORD")

multion_api_key = os.getenv("MULTION_API_KEY")
multion.login(use_api=True, multion_api_key=multion_api_key)

runpod_url = os.getenv("RUNPOD_URL")

image_temp_1 = "https://cdn.sanity.io/images/bj34pdbp/migration/06f44b489e9fea1004ebd8249a0a633f52fd925f-1096x702.png?w=3840&q=75&fit=clip&auto=format"
image_temp_2 = "https://multion-client-screenshots.s3.us-east-2.amazonaws.com/0cea8653-bf81-41ac-84f2-9b08f8f2f2fa_e9209e98-8863-44e4-bc16-0ed46b1e56ca_remote_screenshot.png"


class DevOn:
    def __init__(self, editor_image, browser_image, scratchpad_image):
        self.editor_image = editor_image
        self.browser_image = browser_image
        self.scratchpad_image = scratchpad_image

        self.programmer = multion.create_session(
            {
                # "input": "Create a new directory called multiondev, go into it, create a file called main.py, cat main.py",
                "url": runpod_url,
                "includeScreenshot": True,
            }
        )
        self.programmer_logged_in = False
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
                "url": "https://anotepad.com/",
                "includeScreenshot": True,
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

    def programmer_login(self):
        while True:
            self.programmer = multion.step_session(
                self.programmer["session_id"],
                {
                    "input": "Create a new directory called multiondev, go into it, create a file called main.py, cat main.py"
                    + "\n\n"
                    + programmer_notes,
                    "url": runpod_url,
                    "includeScreenshot": True,
                },
            )
            print(self.programmer)
            # time.sleep(1)
            # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
            # self.editor_image = self.programmer["screenshot"]
            if self.programmer["status"] == "DONE":
                break

        time.sleep(1)
        self.editor_image = self.programmer["screenshot"]

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

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Programmer Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.editor_image}},
                ],
            }
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Researcher Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.browser_image}},
                ],
            }
        )
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is the current state of the Notetaker Intern.",
                    },
                    {"type": "image_url", "image_url": {"url": self.scratchpad_image}},
                ],
            }
        )
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
                        "url": runpod_url,
                        "includeScreenshot": True,
                    },
                )
                print(self.programmer)
                if self.programmer["status"] == "NOT SURE":
                    self.messages.append(
                        {
                            "role": "user",
                            "content": "The Programmer says: {message}\n\nYour next reply will go to the programmer.".format(
                                message=self.programmer["message"]
                            ),
                        }
                    )
                    chat_completion = self.client.chat.completions.create(
                        messages=self.prepare_messages(),
                        model="gpt-4-vision-preview",
                        # max_tokens=200,
                    )
                    action_arg = chat_completion.choices[0].message.content
                    self.messages.append({"role": "assistant", "content": action_arg})
                else:
                    self.messages.append(
                        {
                            "role": "user",
                            "content": "The Programmer says: {message}".format(
                                message=self.programmer["message"]
                            ),
                        }
                    )
                # time.sleep(1)
                # self.editor_image = self.programmer["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.programmer["status"] == "DONE":
                    break
            time.sleep(1)
            self.editor_image = self.programmer["screenshot"]
            return
        elif action_func == "researcher":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.researcher = multion.step_session(
                    self.researcher["session_id"],
                    {
                        "input": action_arg,
                        "url": "https://www.google.com",
                        "includeScreenshot": True,
                    },
                )
                print(self.researcher)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Researcher says: {message}".format(
                            message=self.researcher["message"]
                        ),
                    }
                )
                # time.sleep(1)
                # self.browser_image = self.researcher["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.researcher["status"] == "DONE":
                    break
            time.sleep(1)
            self.browser_image = self.researcher["screenshot"]
            return
        elif action_func == "notetaker":
            action_arg = action.split(" ", 1)[1]
            while True:
                self.notetaker = multion.step_session(
                    self.notetaker["session_id"],
                    {
                        "input": action_arg + notetaker_notes,
                        "url": "https://anotepad.com/",
                        "includeScreenshot": True,
                    },
                )
                print(self.notetaker)
                self.messages.append(
                    {
                        "role": "user",
                        "content": "The Notetaker says: {message}".format(
                            message=self.notetaker["message"]
                        ),
                    }
                )
                # time.sleep(1)
                # self.scratchpad_image = self.notetaker["screenshot"]
                # yield ("", self.editor_image, self.browser_image, self.scratchpad_image)
                if self.notetaker["status"] == "DONE":
                    break
            time.sleep(1)
            self.scratchpad_image = self.notetaker["screenshot"]
            return
        elif action_func == "clarify":
            action_arg = action.split(" ", 1)[1]
            return

    def orchestrator(self):
        if not self.programmer_logged_in:
            self.programmer_login()
            self.programmer_logged_in = True
        messages = self.prepare_messages()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="gpt-4-vision-preview",
            # max_tokens=200,
        )
        response = chat_completion.choices[0].message.content
        action, explanation = response.split("Explanation: ", 1)
        action = action.split("Action: ", 1)[1]

        self.messages.append({"role": "assistant", "content": response})
        self.messages.append(
            {
                "role": "user",
                "content": "The current Plan state is: {plan}".format(plan=self.plan),
            }
        )
        print(self.messages)

        self.execute_action(action)

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
