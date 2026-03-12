
class KombajnRouter:
    def route_for_task(self, task, args, kwargs, **request):
        """
        Dynamic decision maker for task routing.
        
        Priority:
        1. Explicit 'routing_hint' in kwargs (e.g. .apply_async(kwargs={'routing_hint': 'runpod'}))
        2. Task-name based mapping (logical grouping)
        3. Default queue
        """
        
        # 1. Check for explicit hint in kwargs
        # Note: We don't pop it here because Celery routers shouldn't modify kwargs 
        # unless you handle it carefully. Better to just read it.
        routing_hint = kwargs.get('routing_hint')
        if routing_hint:
            return {'queue': f'q_{routing_hint}'}

        # 2. Task-based mapping
        # Heavy Video/CPU tasks
        if any(name in task for name in ['render', 'assemble', 'ffmpeg']):
            return {'queue': 'q_cpu_edit'}
        
        # AI / Vision tasks
        if any(name in task for name in ['analyze', 'vision', 'ai_']):
            return {'queue': 'q_gpu_local'}
            
        # Light / IO tasks
        if any(name in task for name in ['ping', 'notification', 'download']):
            return {'queue': 'q_io'}

        # 3. Default fallback
        return {'queue': 'q_default'}
