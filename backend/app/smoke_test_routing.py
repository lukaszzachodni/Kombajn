import sys
import os
import time
from backend.app.tasks import ping, orchestrate_video_render
from backend.app.celery_app import celery_app

def run_routing_test():
    print("\n--- Kombajn Atomic Routing Self-Evaluation ---")
    
    errors = []
    
    # 1. Test IO Worker Routing
    print("Testing IO Worker (q_io) with ping...")
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

    # 2. Testing Orchestration (Atomic Flow)
    print("\nTesting Orchestration & Parallel Rendering (Fan-Out)...")
    
    minimal_manifest = {
        "width": 640,
        "height": 480,
        "fps": 24,
        "scenes": [
            {
                "comment": "Scene 1",
                "background_color": "#FF0000",
                "duration": 0.5,
                "elements": [{"type": "text", "text": "Scene 1", "duration": 0.5}]
            },
            {
                "comment": "Scene 2",
                "background_color": "#0000FF",
                "duration": 0.5,
                "elements": [{"type": "text", "text": "Scene 2", "duration": 0.5}]
            }
        ]
    }
    
    # Send orchestration task (Stage 2)
    # This task itself should ideally run on q_io or q_default
    res_orch = orchestrate_video_render.apply_async(args=[minimal_manifest])
    print(f"Orchestration Task ID: {res_orch.id}")
    
    try:
        orch_val = res_orch.get(timeout=10)
        chord_id = orch_val.get('task_id')
        print(f"✅ SUCCESS: Orchestration complete. Chord ID: {chord_id}")
        
        # Now wait for the whole chord (Final Assembly)
        # We need to wait for the assembly task result
        print("Waiting for Parallel Scene Rendering and Final Assembly...")
        from celery.result import AsyncResult
        res_final = AsyncResult(chord_id)
        
        # This will block until the assemble_video_task completes
        final_val = res_final.get(timeout=60)
        
        print(f"✅ SUCCESS: Full Atomic Render completed!")
        print(f"Output path: {final_val.get('output_path')}")
        
    except Exception as e:
        print(f"❌ ATOMIC FLOW FAILED: {e}")
        errors.append(f"Atomic Render Error: {e}")

    # Final Evaluation
    print("\n--- Final Report ---")
    if not errors:
        print("🚀 ALL SYSTEMS GO: Atomic Routing and Rendering are perfectly configured.")
        sys.exit(0)
    else:
        print("⚠️ ARCHITECTURAL ERRORS DETECTED:")
        for err in errors:
            print(f"   - {err}")
        sys.exit(1)

if __name__ == "__main__":
    run_routing_test()
