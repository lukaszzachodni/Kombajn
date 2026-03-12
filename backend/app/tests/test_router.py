import pytest
from backend.app.router import KombajnRouter

def test_router_video_tasks():
    router = KombajnRouter()
    
    # Zadania montażowe powinny trafić do q_cpu_edit
    assert router.route_for_task('kombajn.tasks.render_scene', [], {}) == {'queue': 'q_cpu_edit'}
    assert router.route_for_task('kombajn.tasks.assemble_video', [], {}) == {'queue': 'q_cpu_edit'}

def test_router_io_tasks():
    router = KombajnRouter()
    
    # Lekkie zadania powinny trafić do q_io
    assert router.route_for_task('kombajn.tasks.ping', [], {}) == {'queue': 'q_io'}
    assert router.route_for_task('kombajn.tasks.download_asset', [], {}) == {'queue': 'q_io'}

def test_router_routing_hint():
    router = KombajnRouter()
    
    # Hint powinien nadpisać domyślne zachowanie
    kwargs = {'routing_hint': 'runpod'}
    assert router.route_for_task('kombajn.tasks.render_scene', [], kwargs) == {'queue': 'q_runpod'}

def test_router_default_fallback():
    router = KombajnRouter()
    
    # Nieznane zadanie trafia do q_default
    assert router.route_for_task('kombajn.tasks.unknown_action', [], {}) == {'queue': 'q_default'}
