# Code Style Guide

Team coding standards derived from ml-workflow-cloud-functions and dxp-analysis-report projects.

## 🐍 Python Style Standards

### General Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: 120 characters maximum (some projects use 100)
- **Encoding**: UTF-8 with Chinese comments acceptable
- **String formatting**: Use f-strings for string interpolation

### Naming Conventions
```python
# Functions and variables: snake_case
def process_user_data():
    user_count = 0
    
# Classes: PascalCase
class DataProcessor:
    pass
    
# Constants: UPPER_CASE
MAX_RETRY_COUNT = 3
API_ENDPOINT = "https://api.example.com"

# Private methods: leading underscore
def _internal_helper():
    pass
```

### Import Organization
```python
# 1. Standard library imports
import json
import logging
from typing import Dict, List, Optional, Any

# 2. Third-party imports
import pandas as pd
import numpy as np
from flask import Request
import functions_framework

# 3. Local imports
from src.components.core import DataProcessor
from src.utils import tools
from config import settings
```

### Type Hints
```python
# Function signatures with type hints
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process input data and return results."""
    pass

# Optional and Union types
from typing import Optional, Union, List

def get_user(user_id: str) -> Optional[Dict[str, str]]:
    """Retrieve user by ID, return None if not found."""
    pass

# Complex type annotations
def batch_process(
    items: List[Dict[str, Any]], 
    batch_size: int = 100
) -> List[Dict[str, Union[str, int]]]:
    """Process items in batches."""
    pass
```

## 📝 Documentation Standards

### Docstring Format
```python
def calculate_metrics(data: pd.DataFrame, metric_type: str) -> Dict[str, float]:
    """
    計算指定類型的指標
    
    Args:
        data: 包含原始數據的 DataFrame
        metric_type: 指標類型 ('frequency', 'purchase_power', 'user_profile')
        
    Returns:
        Dict: 包含計算結果的字典
        
    Raises:
        ValueError: 當 metric_type 不支援時
        
    Example:
        >>> df = pd.DataFrame({'user_id': [1, 2], 'value': [10, 20]})
        >>> result = calculate_metrics(df, 'frequency')
        >>> print(result['total_users'])
        2
    """
    pass
```

### File Headers
```python
"""
Cloud Function for processing user analytics data

此檔案處理用戶分析數據，包含以下功能：
- 數據預處理和清洗
- 關鍵字頻率計算
- 用戶輪廓生成

Author: Team Data Science
Created: 2024-01-01
Last Modified: 2024-07-22
"""
```

## 🔧 Function Design Patterns

### Cloud Function Entry Points
```python
import functions_framework
from flask import Request
import json
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@functions_framework.http
def main(request: Request) -> tuple[str, int]:
    """
    HTTP Cloud Function 主要進入點
    
    Args:
        request: Flask Request 物件
        
    Returns:
        tuple: (response_body, status_code)
    """
    try:
        if request.method == 'OPTIONS':
            return handle_cors()
        elif request.method == 'POST':
            return handle_post_request(request)
        elif request.method == 'GET':
            return handle_get_request(request)
        else:
            return json.dumps({
                'error': f'不支援的請求方法: {request.method}',
                'status': 'error'
            }), 405
            
    except Exception as e:
        logger.error(f"處理請求時發生錯誤: {str(e)}", exc_info=True)
        return json.dumps({
            'error': '內部伺服器錯誤',
            'status': 'error'
        }), 500
```

### Error Handling Patterns
```python
# Comprehensive error handling
def process_with_retry(data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    """處理數據並支援重試機制"""
    for attempt in range(max_retries):
        try:
            result = expensive_operation(data)
            logger.info(f"處理成功，嘗試次數: {attempt + 1}")
            return result
            
        except TemporaryError as e:
            logger.warning(f"暫時性錯誤 (嘗試 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except PermanentError as e:
            logger.error(f"永久性錯誤: {e}")
            raise
            
    raise RuntimeError("超過最大重試次數")
```

### Logging Standards
```python
import logging
from typing import Dict, Any

# 結構化日誌記錄
logger = logging.getLogger(__name__)

def log_operation(operation: str, data: Dict[str, Any], status: str = "success"):
    """記錄操作日誌"""
    log_entry = {
        "operation": operation,
        "status": status,
        "data_size": len(data) if isinstance(data, (list, dict)) else 1,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if status == "success":
        logger.info(f"操作完成: {operation}", extra=log_entry)
    elif status == "warning":
        logger.warning(f"操作警告: {operation}", extra=log_entry)
    else:
        logger.error(f"操作失敗: {operation}", extra=log_entry)
```

## 📊 Data Processing Patterns

### Pandas Operations
```python
import pandas as pd
from typing import List, Dict, Any

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """標準化數據清洗流程"""
    # 移除重複值
    df = df.drop_duplicates()
    
    # 處理缺失值
    df = df.dropna(subset=['required_column'])
    
    # 數據類型轉換
    df['date_column'] = pd.to_datetime(df['date_column'])
    df['numeric_column'] = pd.to_numeric(df['numeric_column'], errors='coerce')
    
    # 記錄清洗結果
    logger.info(f"數據清洗完成，剩餘記錄數: {len(df)}")
    
    return df

def batch_process_dataframe(
    df: pd.DataFrame, 
    process_func: callable, 
    batch_size: int = 1000
) -> List[Dict[str, Any]]:
    """批量處理大型 DataFrame"""
    results = []
    total_batches = len(df) // batch_size + (1 if len(df) % batch_size else 0)
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i + batch_size]
        batch_result = process_func(batch)
        results.extend(batch_result)
        
        logger.info(f"處理批次 {i//batch_size + 1}/{total_batches}")
    
    return results
```

### Async Processing Patterns
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

async def process_async_batch(
    items: List[Dict[str, Any]], 
    semaphore_limit: int = 10
) -> List[Dict[str, Any]]:
    """異步批量處理"""
    semaphore = asyncio.Semaphore(semaphore_limit)
    
    async def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            # 處理單個項目
            result = await expensive_async_operation(item)
            return result
    
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 處理異常
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"處理項目 {i} 失敗: {result}")
        else:
            successful_results.append(result)
    
    return successful_results
```

## 🧪 Testing Standards

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from src.main import process_data

class TestDataProcessing:
    """數據處理功能測試"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.sample_data = {
            'user_id': '12345',
            'events': [{'type': 'view', 'timestamp': '2024-01-01'}]
        }
    
    def test_process_data_success(self):
        """測試正常數據處理"""
        result = process_data(self.sample_data)
        
        assert result['status'] == 'success'
        assert 'processed_data' in result
        assert len(result['processed_data']) > 0
    
    def test_process_data_empty_input(self):
        """測試空輸入處理"""
        with pytest.raises(ValueError, match="輸入數據不能為空"):
            process_data({})
    
    @patch('src.main.external_api_call')
    def test_process_data_with_mock(self, mock_api):
        """測試外部 API 調用的模擬"""
        mock_api.return_value = {'status': 'ok', 'data': []}
        
        result = process_data(self.sample_data)
        
        mock_api.assert_called_once()
        assert result['status'] == 'success'
```

### Integration Test Patterns
```python
import pytest
from google.cloud import storage
from src.utils.gcs_utils import upload_to_gcs

@pytest.mark.integration
class TestGCSIntegration:
    """GCS 整合測試"""
    
    @pytest.fixture
    def gcs_client(self):
        """GCS 客戶端 fixture"""
        return storage.Client()
    
    def test_upload_file_to_gcs(self, gcs_client):
        """測試文件上傳到 GCS"""
        test_data = "測試數據內容"
        bucket_name = "test-bucket"
        file_path = "test/file.txt"
        
        result = upload_to_gcs(test_data, bucket_name, file_path)
        
        assert result['status'] == 'success'
        
        # 驗證文件確實上傳
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        assert blob.exists()
        
        # 清理測試數據
        blob.delete()
```

## 🔧 Configuration Management

### Environment Configuration
```python
import os
from typing import Optional

class Config:
    """應用程式配置管理"""
    
    # GCP 設定
    PROJECT_ID: str = os.getenv('GCP_PROJECT_ID', 'tagtoo-ml-workflow')
    BUCKET_NAME: str = os.getenv('GCS_BUCKET_NAME', 'default-bucket')
    
    # API 設定
    API_TIMEOUT: int = int(os.getenv('API_TIMEOUT', '30'))
    MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
    
    # 數據處理設定
    BATCH_SIZE: int = int(os.getenv('BATCH_SIZE', '1000'))
    PARALLEL_WORKERS: int = int(os.getenv('PARALLEL_WORKERS', '4'))
    
    @classmethod
    def validate(cls) -> bool:
        """驗證必要的配置是否存在"""
        required_vars = ['GCP_PROJECT_ID']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"缺少必要的環境變數: {missing_vars}")
        
        return True
```