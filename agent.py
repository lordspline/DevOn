class DevOn:
    def __init__(self):
        self.editor_image = "https://cdn.sanity.io/images/bj34pdbp/migration/06f44b489e9fea1004ebd8249a0a633f52fd925f-1096x702.png?w=3840&q=75&fit=clip&auto=format"
        self.browser_image = "https://cdn.sanity.io/images/bj34pdbp/migration/06f44b489e9fea1004ebd8249a0a633f52fd925f-1096x702.png?w=3840&q=75&fit=clip&auto=format"
        self.scratchpad_image = "https://cdn.sanity.io/images/bj34pdbp/migration/06f44b489e9fea1004ebd8249a0a633f52fd925f-1096x702.png?w=3840&q=75&fit=clip&auto=format"
        self.done = True

    def orchestrator(self):
        self.done = True
        return "ungus"

    def run(self, prompt):
        self.done = False
        while not self.done:
            curr_response = self.orchestrator()
            yield (
                curr_response,
                self.editor_image,
                self.browser_image,
                self.scratchpad_image,
            )
