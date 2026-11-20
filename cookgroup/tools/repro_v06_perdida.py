import sys; sys.path.insert(0,"src"); sys.path.insert(0,"tests")
import tempfile, pathlib
from cookgroup.config import MonitorConfig
from cookgroup.market import FileMarketProvider
from cookgroup.pipeline import run_cycle
from cookgroup.store import Store
from test_core import FIX, FakeSource, with_available
import cookgroup.ratelimit as rl; rl.DEFAULT_MIN_INTERVAL=0
t=pathlib.Path(tempfile.mkdtemp()); cfg=MonitorConfig("t","shopify","TestShop","https://shop.invalid")
got=[]; down=[False]
def send(p):
    if down[0]: raise RuntimeError("Discord 503")
    got.append(p); return "id"
st=Store(t/"s.db"); mk=FileMarketProvider(t/"none.json")
src=FakeSource([FIX, with_available({1}), with_available({1})])
run_cycle(cfg,{},src,st,mk,send)
down[0]=True
try: print("ciclo con Discord caído:", run_cycle(cfg,{},src,st,mk,send))
except Exception as e: print("ciclo con Discord caído lanzó:", type(e).__name__, e)
down[0]=False
print("Discord vuelve:", run_cycle(cfg,{},src,st,mk,send)); print("avisos recibidos tras recuperar:", len(got))
