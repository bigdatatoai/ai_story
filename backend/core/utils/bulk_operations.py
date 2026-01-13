"""
批量操作工具类
职责: 提供高效的批量数据操作
"""

from django.db import transaction
import logging

logger = logging.getLogger(__name__)


class BulkOperationManager:
    """批量操作管理器"""
    
    DEFAULT_BATCH_SIZE = 100
    MAX_BATCH_SIZE = 1000
    
    @classmethod
    def bulk_create(cls, model_class, data_list, batch_size=None, ignore_conflicts=False):
        """
        批量创建数据
        
        Args:
            model_class: 模型类
            data_list: 数据列表（字典或模型实例）
            batch_size: 批次大小
            ignore_conflicts: 是否忽略冲突
        
        Returns:
            list: 创建的实例列表
        """
        if not data_list:
            return []
        
        batch_size = batch_size or cls.DEFAULT_BATCH_SIZE
        if batch_size > cls.MAX_BATCH_SIZE:
            batch_size = cls.MAX_BATCH_SIZE
        
        try:
            # 转换为模型实例
            instances = []
            for data in data_list:
                if isinstance(data, dict):
                    instances.append(model_class(**data))
                else:
                    instances.append(data)
            
            # 批量创建
            with transaction.atomic():
                created = model_class.objects.bulk_create(
                    instances,
                    batch_size=batch_size,
                    ignore_conflicts=ignore_conflicts
                )
            
            logger.info(f"批量创建成功: {model_class.__name__}, 数量: {len(created)}")
            return created
            
        except Exception as e:
            logger.error(f"批量创建失败: {model_class.__name__} - {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def bulk_update(cls, instances, fields, batch_size=None):
        """
        批量更新数据
        
        Args:
            instances: 模型实例列表
            fields: 要更新的字段列表
            batch_size: 批次大小
        
        Returns:
            int: 更新的数量
        """
        if not instances or not fields:
            return 0
        
        batch_size = batch_size or cls.DEFAULT_BATCH_SIZE
        if batch_size > cls.MAX_BATCH_SIZE:
            batch_size = cls.MAX_BATCH_SIZE
        
        try:
            model_class = instances[0].__class__
            
            with transaction.atomic():
                model_class.objects.bulk_update(
                    instances,
                    fields,
                    batch_size=batch_size
                )
            
            logger.info(f"批量更新成功: {model_class.__name__}, 数量: {len(instances)}")
            return len(instances)
            
        except Exception as e:
            logger.error(f"批量更新失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def bulk_delete(cls, queryset, soft_delete=True, batch_size=None):
        """
        批量删除数据
        
        Args:
            queryset: 查询集
            soft_delete: 是否软删除
            batch_size: 批次大小
        
        Returns:
            int: 删除的数量
        """
        if not queryset.exists():
            return 0
        
        batch_size = batch_size or cls.DEFAULT_BATCH_SIZE
        
        try:
            if soft_delete:
                # 软删除
                count = queryset.count()
                with transaction.atomic():
                    queryset.update(is_deleted=True)
                
                logger.info(f"批量软删除成功: 数量: {count}")
                return count
            else:
                # 硬删除
                with transaction.atomic():
                    count, _ = queryset.delete()
                
                logger.info(f"批量硬删除成功: 数量: {count}")
                return count
                
        except Exception as e:
            logger.error(f"批量删除失败: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def batch_process(cls, queryset, process_func, batch_size=None):
        """
        批量处理数据
        
        Args:
            queryset: 查询集
            process_func: 处理函数，接收实例列表作为参数
            batch_size: 批次大小
        
        Returns:
            dict: 处理结果统计
        """
        batch_size = batch_size or cls.DEFAULT_BATCH_SIZE
        
        total = queryset.count()
        processed = 0
        failed = 0
        
        logger.info(f"开始批量处理: 总数={total}, 批次大小={batch_size}")
        
        try:
            # 分批处理
            for i in range(0, total, batch_size):
                batch = list(queryset[i:i + batch_size])
                
                try:
                    with transaction.atomic():
                        process_func(batch)
                    processed += len(batch)
                    logger.debug(f"批次处理成功: {i}-{i+len(batch)}")
                    
                except Exception as e:
                    failed += len(batch)
                    logger.error(f"批次处理失败: {i}-{i+len(batch)} - {str(e)}")
            
            result = {
                'total': total,
                'processed': processed,
                'failed': failed,
                'success_rate': round((processed / total) * 100, 2) if total > 0 else 0
            }
            
            logger.info(f"批量处理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"批量处理异常: {str(e)}", exc_info=True)
            raise


def chunked_queryset(queryset, chunk_size=1000):
    """
    将查询集分块迭代
    
    Args:
        queryset: Django查询集
        chunk_size: 块大小
    
    Yields:
        list: 每块的数据列表
    
    Usage:
        for chunk in chunked_queryset(User.objects.all(), 100):
            process_users(chunk)
    """
    start = 0
    while True:
        chunk = list(queryset[start:start + chunk_size])
        if not chunk:
            break
        yield chunk
        start += chunk_size
