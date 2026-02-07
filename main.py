#%%
import sys
sys.path.insert(0, "rlib")
from rlib.useful.LibsDB import LibsDB
print(LibsDB.runBasic())
# %%
from rlib.useful.Path import Path
# %%

uploader = CursorChatsUploader()

uploader.upload()
#%%
from rlib.timeline.t2026.directus_chat_sync import DirectusTable
table = DirectusTable()

table.initialize_headers()

#%%

# %%
table.set_collection("raja_daily_logs")
res = table.get_all(["id", "content", "type", "on_date"])
res
# %%
table.set_collection("raja_logs_type")
types = table.get_all(["id", "name"])
types
# %%
worklogs = [r for r in res if r["type"] == 4]
worklogs
# %%
logs = ""
for log in worklogs[2:]:
    logs += f"{log['on_date']}\n-----\n{log['content']}\n================\n\n\n\n"
print(logs)
# %%
table.set_collection("raja_daily_logs")
table.post({"content": logs, "type": 4, "on_date": "2026-01-27"})
# %%

