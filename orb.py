from openai import OpenAI
from prompts.orchestrator import orchestrator_prompt
from prompts.programmer import programmer_notes
from prompts.notetaker import notetaker_notes
from prompts.orb import orb_prompt
from dotenv import load_dotenv
import time
import os
from playwright.sync_api import sync_playwright
import uuid
import base64
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import anthropic


load_dotenv(".env.local")

replit_email = os.getenv("REPLIT_EMAIL")
replit_password = os.getenv("REPLIT_PASSWORD")

temp_image = "https://multion-client-screenshots.s3.us-east-2.amazonaws.com/0cea8653-bf81-41ac-84f2-9b08f8f2f2fa_e9209e98-8863-44e4-bc16-0ed46b1e56ca_remote_screenshot.png"


class Orb:
    def __init__(self, start_page="https://www.google.com/"):

        self.done = True
        self.task = ""
        self.plan = ""
        self.scratchpad = ""
        self.messages = []
        self.client = OpenAI()
        self.claude = anthropic.Anthropic()

        # playwright stuff
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.goto(start_page)

        self.mouse_pos = (640, 360)
        self.page.mouse.move(self.mouse_pos[0], self.mouse_pos[1])

        self.take_screenshot()

    # def __del__(self):
    #     self.browser.contexts[0].pages[0].close()
    #     self.browser.close()
    #     self.p.stop()

    def take_screenshot(self):
        self.screenshot = os.path.join("screenshots", str(uuid.uuid4()) + ".png")
        self.page.screenshot(path=self.screenshot)
        time.sleep(1)
        img = plt.imread(self.screenshot)
        print(img.shape)
        H, W, C = img.shape
        # img[0:H:40] = [1, 0, 0, 1]
        # img[:, 0:W:60] = [1, 0, 0, 1]
        img[
            self.mouse_pos[1] - 6 : self.mouse_pos[1] + 6,
            self.mouse_pos[0] - 6 : self.mouse_pos[0] + 6,
        ] = [1, 0, 0, 1]
        fig = plt.figure(figsize=(12.8, 7.2))
        ax = fig.add_axes([0, 1, 1, 1])
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=60))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(base=40))
        ax.imshow(img)
        plt.savefig(self.screenshot, bbox_inches="tight", dpi=250)
        # plt.imsave(self.screenshot, img)

    def encode_screenshot(self):
        with open(self.screenshot, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def simplified_dom(self):
        self.page.wait_for_load_state("domcontentloaded")
        snapshot = self.page.evaluate(
            """() => {
            
                const isVisible = (elem) => {
                    const style = getComputedStyle(elem);
                    if (style.display === 'none') return false;
                    if (style.visibility !== 'visible') return false;
                    if (style.opacity < 0.1) return false;
                    return true;
                }

                var wl = window.pageXOffset
                var wt = window.pageYOffset
                var wr = window.pageXOffset + window.screen.width
                var wb = window.pageYOffset + window.screen.height 

                var allowedTags = ["A", "INPUT", "BUTTON", "TEXTAREA", "P", "SPAN", "SELECT", "LI", "IMG"]
                var allowedAttributes = ['aria-label', 'name', 'type', 'placeholder', 'value', 'role', 'title']

                var all = document.getElementsByTagName("*");
                var snapshot = [];

                var current_id = 0
                for (var i=0, max=all.length; i < max; i++) {
                    var rect = all[i].getBoundingClientRect()
                    var l = rect['left']
                    var t = rect['top']
                    var r = rect['right']
                    var b = rect['bottom']

                    if (Math.max(l, r) < wl || Math.min(l, r) > wr || Math.max(t, b) < wt || Math.min(t, b) > wb || (l===0 && t===0 && r===0 && b===0) || (r<0||b<0)) {
                        continue
                    }

                    if (allowedTags.includes(all[i].tagName) || all[i].getAttribute('onclick')!=null || all[i].getAttribute('href')!=null) {
                        var node = all[i].cloneNode()

                        // adding attributes
                        var attrString = " "
                        if (node.hasAttributes()) {
                            var attributes = node.attributes
                            for (var j=0; j<attributes.length; j++) {
                                if (attributes[j].name === "id") {
                                    attrString += "id=" + attributes[j].value + " "
                                }
                                else if (allowedAttributes.includes(attributes[j].name) && attributes[j].value !== "") {
                                    attrString += attributes[j].name + "='" + attributes[j].value + "' "
                                }
                            }
                        }

                        var bboxString = "center_x=" + Math.floor((l+r)/2) + " center_y=" + Math.floor((t+b)/2) + " left=" + Math.floor(l) + " top=" + Math.floor(t) + " right=" + Math.floor(r) + " bottom=" + Math.floor(b)

                        var nodeValue = all[i].textContent || all[i].innerText
                        if (node.tagName === "INPUT" && node['type'] === "text") {
                            nodeValue = all[i].value
                        }
                        if (node.tagName === "TEXTAREA") {
                            nodeValue = all[i].value
                        }
                        if (node.tagName === "BUTTON") {
                            if (all[i].disabled === true) {
                                nodeValue += " (This Button is Disabled)"
                            }
                        }
                        if ((node.tagName === "P" || node.tagName === "SPAN") && (nodeValue.toString() === "")) {
                            continue
                        }

                        if (!isVisible(all[i])) {
                            nodeValue += " (This Element is Not Visible)"
                        }

                        // construct node string
                        var nodeString = "<" + node.tagName + " " + bboxString + " " + "z=" + getComputedStyle(all[i]).zIndex + " " + attrString + ">" + nodeValue + "</" + node.tagName + ">"
                        // if (node.tagName != 'BUTTON' && (node.getAttribute('onclick')!=null || node.getAttribute('href')!=null)) {
                        //     nodeString = "<" + "BUTTON" + " id=" + current_id + attrString + bboxString + ">" + nodeValue + "</" + "BUTTON" + ">"
                        // }

                        // output
                        snapshot.push(nodeString)

                        // assign id to actual element so we can interact with it
                        all[i].dataset.miscninja_id = current_id
                        current_id += 1
                    }
                }
                return snapshot 
        }"""
        )
        print("\n".join(snapshot))
        return "\n".join(snapshot)

    def prepare_messages(self, type="gpt"):
        if type == "gpt":
            messages = [
                {"role": "user", "content": orb_prompt},
                {
                    "role": "user",
                    "content": "The Task given to you is: {task}".format(
                        task=self.task
                    ),
                },
            ]

            for message in self.messages:
                messages.append(message)

            messages.append(
                {
                    "role": "user",
                    "content": "The current Plan state is: {plan}".format(
                        plan=self.plan
                    ),
                },
            )

            messages.append(
                {
                    "role": "user",
                    "content": "The current Scratchpad state is: {scratchpad}".format(
                        scratchpad=self.scratchpad
                    ),
                },
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is the current state of the Browser. The red dot (square) shows the current mouse position. The current mouse position is {x}, {y}.".format(
                                x=self.mouse_pos[0], y=self.mouse_pos[1]
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.encode_screenshot()}",
                            },
                        },
                        {
                            "type": "text",
                            "text": "The current simplified DOM corresponding to this screenshot is as follows:\n\n{dom}".format(
                                dom=self.simplified_dom()
                            ),
                        },
                    ],
                }
            )
        return messages

    def execute_action(self, action):

        if action[:7] != "keytype":
            action = action.replace("\n", "")

        action_func = action.split(" ", 1)[0]

        if action_func == "submit":
            self.done = True
            return
        elif action_func == "clarify":
            action_arg = action.split(" ", 1)[1]
            return
        elif action_func == "keypress":
            action_arg = action.split(" ", 1)[1]
            self.page.keyboard.press(action_arg)
            return
        elif action_func == "keytype":
            action_arg = action.split(" ", 1)[1]
            print(action_arg.split("\n"))
            split = action_arg.split("\n")
            if len(split) == 1 or (len(split) == 2 and split[1] == ""):
                print("yay")
                self.page.keyboard.type(action_arg)
                return
            for line in action_arg.split("\n"):
                if line == "":
                    self.page.keyboard.press("Enter")
                else:
                    self.page.keyboard.type(line)
                    self.page.keyboard.press("Enter")
            return
        elif action_func == "mouseclick":
            action_args = action.split(" ")[1], action.split(" ")[2]
            self.page.mouse.click(
                int(action_args[0]),
                int(action_args[1]),
            )
            self.mouse_pos = (
                int(action_args[0]),
                int(action_args[1]),
            )
            return
        elif action_func == "mousedoubleclick":
            action_args = action.split(" ")[1], action.split(" ")[2]
            self.page.mouse.dblclick(
                int(action_args[0]),
                int(action_args[1]),
            )
            self.mouse_pos = (
                int(action_args[0]),
                int(action_args[1]),
            )
            return
        elif action_func == "mousehover":
            action_args = action.split(" ")[1], action.split(" ")[2]
            self.page.mouse.move(
                int(action_args[0]),
                int(action_args[1]),
            )
            self.mouse_pos = (
                int(action_args[0]),
                int(action_args[1]),
            )
            return
        elif action_func == "update_plan":
            action_arg = action.split(" ", 1)[1]
            self.plan = action_arg
            return
        elif action_func == "scratchpad":
            action_arg = action.split(" ", 1)[1]
            self.scratchpad = action_arg
            return

    def orchestrator(self):
        messages = self.prepare_messages()
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="gpt-4-vision-preview",
        )
        response = chat_completion.choices[0].message.content
        # response = self.claude.messages.create(
        #     model="claude-3-opus-20240229", messages=messages, max_tokens=1024
        # )
        action, explanation = response.split("Explanation: ", 1)
        action = action.split("Action: ", 1)[1]

        self.messages.append({"role": "assistant", "content": response})
        # print(self.messages)

        print(action)
        self.execute_action(action)
        time.sleep(1)
        self.take_screenshot()

        # temp
        # self.done = True
        return explanation

    def run(self, prompt):
        self.done = False
        self.task = prompt
        while not self.done:
            curr_response = self.orchestrator()
            yield (curr_response, self.screenshot)


if __name__ == "__main__":
    # demo.queue()
    # demo.launch()

    orb = Orb("https://replit.com/login")
    for r in orb.run(
        "log in using the email multiontemp@gmail.com and password multiontemp, create a python repl (remember to select the python language option in the template dropdown) giving it an appropriate name. Then create a new file called temp.py. Then put some basic hello world fastapi server code into it and run it."
    ):
        print(r)

    # orb = Orb("https://anotepad.com/")
    # for r in orb.run(
    #     "title the note fastapi temp and write some basic hello world server fastapi code in the notepad."
    # ):
    #     print(r)
