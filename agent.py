from openai import OpenAI
from prompts.orchestrator import orchestrator_prompt
from dotenv import load_dotenv
import time

load_dotenv(".env.local")


class DevOn:
    def __init__(self, editor_image, browser_image, scratchpad_image):
        self.editor_image = editor_image
        self.browser_image = browser_image
        self.scratchpad_image = scratchpad_image
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
            time.sleep(5)
