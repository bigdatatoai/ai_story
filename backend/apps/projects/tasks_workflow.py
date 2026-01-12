"""
工作流执行任务
"""

import logging
from typing import Dict, Any
from django.utils import timezone

from config.celery import app
from apps.projects.models_workflow import ProjectWorkflow, WorkflowExecution
from core.workflow.workflow_engine import WorkflowEngine
from core.redis_client import RedisStreamPublisher

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=0)
def execute_workflow_task(self, workflow_id: str, execution_id: str) -> Dict[str, Any]:
    """
    执行工作流任务
    
    Args:
        workflow_id: 工作流ID
        execution_id: 执行记录ID
    """
    try:
        # 获取工作流和执行记录
        workflow = ProjectWorkflow.objects.get(id=workflow_id)
        execution = WorkflowExecution.objects.get(id=execution_id)
        
        # 更新执行状态
        execution.status = 'running'
        execution.started_at = timezone.now()
        execution.save()
        
        # 创建 Redis 发布器
        publisher = RedisStreamPublisher(workflow_id, 'workflow')
        
        # 创建执行引擎
        engine = WorkflowEngine()
        engine.load_workflow(workflow.workflow_data)
        
        # 定义进度回调
        def progress_callback(node_id: str, status: str, result: Any):
            """节点执行进度回调"""
            # 更新工作流当前节点
            workflow.current_node_id = node_id
            workflow.execution_results[node_id] = {
                'status': status,
                'result': result,
                'timestamp': timezone.now().isoformat()
            }
            workflow.save()
            
            # 发布进度到 Redis
            publisher.publish_stage_update(
                status=status,
                progress=0,
                message=f'节点 {node_id} {status}',
                metadata={
                    'node_id': node_id,
                    'result': result
                }
            )
            
            # 添加日志
            execution.logs.append({
                'timestamp': timezone.now().isoformat(),
                'node_id': node_id,
                'level': 'info',
                'message': f'节点状态: {status}'
            })
            execution.save()
        
        # 执行工作流
        logger.info(f"开始执行工作流: {workflow_id}")
        result = engine.execute(callback=progress_callback)
        
        # 更新执行结果
        if result['status'] == 'completed':
            execution.status = 'completed'
            execution.results = result['results']
            workflow.status = 'completed'
            
            publisher.publish_done(
                result=result['results'],
                metadata={'workflow_id': workflow_id}
            )
        else:
            execution.status = 'failed'
            execution.error_message = result.get('error', '未知错误')
            workflow.status = 'failed'
            
            publisher.publish_error(result.get('error', '未知错误'))
        
        execution.completed_at = timezone.now()
        execution.save()
        workflow.save()
        
        logger.info(f"工作流执行完成: {workflow_id}, 状态: {execution.status}")
        
        return {
            'success': execution.status == 'completed',
            'execution_id': execution_id,
            'status': execution.status,
            'results': execution.results
        }
        
    except Exception as e:
        error_msg = f"工作流执行失败: {str(e)}"
        logger.exception(error_msg)
        
        # 更新执行记录
        try:
            execution.status = 'failed'
            execution.error_message = error_msg
            execution.completed_at = timezone.now()
            execution.save()
            
            workflow.status = 'failed'
            workflow.save()
        except:
            pass
        
        return {
            'success': False,
            'error': error_msg
        }
    finally:
        publisher.close()


@app.task(bind=True)
def resume_workflow_task(self, workflow_id: str) -> Dict[str, Any]:
    """
    恢复暂停的工作流
    
    Args:
        workflow_id: 工作流ID
    """
    try:
        workflow = ProjectWorkflow.objects.get(id=workflow_id)
        
        if workflow.status != 'paused':
            return {
                'success': False,
                'error': '工作流未暂停'
            }
        
        # 创建新的执行记录
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status='running',
            started_at=timezone.now()
        )
        
        # 从当前节点继续执行
        engine = WorkflowEngine()
        engine.load_workflow(workflow.workflow_data)
        
        # 恢复之前的结果
        engine.results = workflow.execution_results
        
        # 找到当前节点在执行顺序中的位置
        current_index = 0
        if workflow.current_node_id:
            try:
                current_index = engine.execution_order.index(workflow.current_node_id)
            except ValueError:
                current_index = 0
        
        # 从下一个节点开始执行
        remaining_nodes = engine.execution_order[current_index + 1:]
        
        publisher = RedisStreamPublisher(workflow_id, 'workflow')
        
        def progress_callback(node_id: str, status: str, result: Any):
            workflow.current_node_id = node_id
            workflow.execution_results[node_id] = {
                'status': status,
                'result': result
            }
            workflow.save()
            
            publisher.publish_stage_update(
                status=status,
                progress=0,
                message=f'节点 {node_id} {status}',
                metadata={'node_id': node_id}
            )
        
        # 执行剩余节点
        for node_id in remaining_nodes:
            node = engine.nodes[node_id]
            engine._set_node_inputs(node)
            
            try:
                outputs = node.execute()
                engine.results[node_id] = {
                    'status': 'completed',
                    'outputs': outputs
                }
                progress_callback(node_id, 'completed', outputs)
            except Exception as e:
                error_msg = f"节点执行失败: {str(e)}"
                engine.results[node_id] = {
                    'status': 'failed',
                    'error': error_msg
                }
                progress_callback(node_id, 'failed', {'error': error_msg})
                raise
        
        # 更新状态
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.results = engine.results
        execution.save()
        
        workflow.status = 'completed'
        workflow.save()
        
        publisher.publish_done(result=engine.results)
        publisher.close()
        
        return {
            'success': True,
            'execution_id': str(execution.id)
        }
        
    except Exception as e:
        logger.exception(f"恢复工作流失败: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
