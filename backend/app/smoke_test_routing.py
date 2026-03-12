import sys
from backend.app.tasks import ping, render_scene
from backend.app.celery_app import celery_app

def run_routing_test():
    print("\n--- Kombajn Routing Self-Evaluation ---")
    
    errors = []
    
    # 1. Test IO Worker Routing
    print("Testing IO Worker (q_io)...")
    res_ping = ping.apply_async()
    try:
        ping_val = res_ping.get(timeout=15)
        worker = ping_val.get('worker', 'unknown')
        if 'worker_io' in worker:
            print(f"✅ SUCCESS: 'ping' handled by expected worker: {worker}")
        else:
            errors.append(f"WRONG WORKER: 'ping' was handled by '{worker}', but expected 'worker_io'")
    except Exception as e:
        errors.append(f"FAILED: 'ping' task did not complete: {e}")

    # Testing Editor Worker (q_cpu_edit)
    print("\nTesting Editor Worker (q_cpu_edit)...")
    valid_scene = {
        "background": {"type": "color", "color": [0, 0, 0], "duration": 0.5},
        "elements": []
    }
    res_render = render_scene.apply_async(args=["smoke_test", valid_scene, 640, 480, 24, 1])
    try:
        render_val = res_render.get(timeout=30)
        worker = render_val.get('worker', 'unknown')
        if 'worker_editor' in worker:
            print(f"✅ SUCCESS: 'render_scene' handled by expected worker: {worker}")
        else:
            errors.append(f"WRONG WORKER: 'render_scene' was handled by '{worker}', but expected 'worker_editor'")
    except Exception as e:
        errors.append(f"FAILED: 'render_scene' task did not complete: {e}")

    # Final Evaluation
    print("\n--- Final Report ---")
    if not errors:
        print("🚀 ALL SYSTEMS GO: Routing is perfectly configured.")
        print("Specialist workers are correctly picking up their designated tasks.")
        sys.exit(0)
    else:
        print("❌ ROUTING ERROR: Issues detected in task distribution:")
        for err in errors:
            print(f"   - {err}")
        print("\nPlease check your KombajnRouter and Docker worker configurations.")
        sys.exit(1)

if __name__ == "__main__":
    run_routing_test()
