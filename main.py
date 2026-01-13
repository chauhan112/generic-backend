#%% 
import os
import sys
sys.path.append("rlib")
from handlers.githubHandler import MainGitHubHandler
from handlers.controller import ApiController
controller = ApiController()
controller.add_handler(MainGitHubHandler.get_handler())
controller.set_base_path("/api")
controller.set_path("/api/github/search")

#%% 
controller.set_input({
    "repo": "git@github.com:chauhan112/Rlib.git",
    "word": "a",
    "extensions": [
        ".py"
    ],
    "case": False,
    "reg": False
})
print(controller.process())
# %%
