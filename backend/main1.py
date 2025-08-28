import asyncio
import json
import logging
import multiprocessing as mp
import signal
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from enum import Enum
from multiprocessing import Manager, Process, Queue
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class ProcessStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ProcessType(str, Enum):
    READ = "read"
    TRANSFORM = "transform"
    ENRICH = "enrich"
    GENERATE = "generate"

class APIError(BaseModel):
    error_code: str
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[APIError] = None
    metadata: Optional[Dict[str, Any]] = None

class ProcessProgress(BaseModel):
    process_id: str
    progress_percentage: float = Field(ge=0, le=100)
    current_stage: str
    estimated_completion: Optional[datetime] = None
    logs: List[str] = []
    stages_completed: List[str] = []
    current_stage_details: Optional[str] = None

class ProcessSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    estimated_duration: int  # in seconds
    output_format: str
    stages: List[str]
    required_params: List[str] = []

class ProcessRequest(BaseModel):
    parameters: Dict[str, Any] = {}
    
    @validator('parameters')
    def validate_parameters(cls, v):
        # Add basic parameter validation here
        return v

class ProcessInfo(BaseModel):
    process_id: str
    name: str
    status: ProcessStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    data_count: Optional[int] = None
    progress: Optional[ProcessProgress] = None
    duration_seconds: Optional[float] = None

class ProcessResult(BaseModel):
    process_id: str
    process_name: str
    status: ProcessStatus
    result: Optional[Dict[str, Any]] = None
    data_count: Optional[int] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = {}

# ============================================================================
# Process Implementations
# ============================================================================

class DataProcessor:
    """Base class for all data processors"""
    
    def __init__(self, process_id: str, progress_queue: Queue):
        self.process_id = process_id
        self.progress_queue = progress_queue
        self.stages = []
        
    def update_progress(self, stage: str, percentage: float, details: str = None, logs: List[str] = None):
        """Update process progress"""
        try:
            progress = {
                'process_id': self.process_id,
                'current_stage': stage,
                'progress_percentage': percentage,
                'current_stage_details': details,
                'logs': logs or [],
                'timestamp': datetime.now().isoformat()
            }
            self.progress_queue.put(progress)
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")

class ReadProcessor(DataProcessor):
    """Data reading processor"""
    
    def __init__(self, process_id: str, progress_queue: Queue):
        super().__init__(process_id, progress_queue)
        self.stages = ["initializing", "connecting", "reading", "validating", "completed"]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute read process"""
        
        # Stage 1: Initializing
        self.update_progress("initializing", 10, "Setting up data source connections")
        time.sleep(1)
        
        # Stage 2: Connecting
        self.update_progress("connecting", 25, "Establishing connection to data source")
        time.sleep(2)
        
        # Stage 3: Reading
        self.update_progress("reading", 60, "Reading data from source")
        
        # Simulate reading data
        source_type = parameters.get('source_type', 'database')
        batch_size = parameters.get('batch_size', 100)
        total_records = parameters.get('total_records', 1000)
        
        data = []
        for i in range(total_records):
            if i % (total_records // 4) == 0:  # Update progress 4 times
                progress = 60 + (i / total_records) * 30
                self.update_progress("reading", progress, f"Read {i}/{total_records} records")
            
            record = {
                "id": i,
                "source_type": source_type,
                "data_field_1": f"value_{i}",
                "data_field_2": i * 1.5,
                "timestamp": datetime.now().isoformat(),
                "batch_id": i // batch_size
            }
            data.append(record)
            
            # Simulate processing time
            if i % 100 == 0:
                time.sleep(0.1)
        
        # Stage 4: Validating
        self.update_progress("validating", 95, "Validating read data")
        time.sleep(1)
        
        # Stage 5: Completed
        self.update_progress("completed", 100, f"Successfully read {len(data)} records")
        
        return {
            "operation": "read",
            "source_type": source_type,
            "records": data,
            "metadata": {
                "total_records": len(data),
                "batch_size": batch_size,
                "source_info": {"type": source_type, "connected_at": datetime.now().isoformat()}
            }
        }

class TransformProcessor(DataProcessor):
    """Data transformation processor"""
    
    def __init__(self, process_id: str, progress_queue: Queue):
        super().__init__(process_id, progress_queue)
        self.stages = ["preparing", "analyzing", "transforming", "optimizing", "completed"]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute transform process"""
        
        # Stage 1: Preparing
        self.update_progress("preparing", 15, "Preparing transformation rules")
        time.sleep(1)
        
        # Stage 2: Analyzing
        self.update_progress("analyzing", 30, "Analyzing data structure")
        time.sleep(2)
        
        # Stage 3: Transforming
        self.update_progress("transforming", 70, "Applying transformations")
        
        # Simulate transformation
        transform_type = parameters.get('transform_type', 'normalize')
        total_records = parameters.get('total_records', 1000)
        
        transformed_data = []
        for i in range(total_records):
            if i % (total_records // 5) == 0:
                progress = 30 + (i / total_records) * 40
                self.update_progress("transforming", progress, f"Transformed {i}/{total_records} records")
            
            record = {
                "transformed_id": f"T_{i:06d}",
                "original_id": i,
                "transform_type": transform_type,
                "normalized_value": round((i * 2.5) / 100, 4),
                "category": f"cat_{i % 10}",
                "processed_at": datetime.now().isoformat(),
                "transformation_rules": ["normalize", "categorize", "timestamp"]
            }
            transformed_data.append(record)
            
            if i % 50 == 0:
                time.sleep(0.05)
        
        # Stage 4: Optimizing
        self.update_progress("optimizing", 85, "Optimizing transformed data")
        time.sleep(1)
        
        # Stage 5: Completed
        self.update_progress("completed", 100, f"Successfully transformed {len(transformed_data)} records")
        
        return {
            "operation": "transform",
            "transform_type": transform_type,
            "records": transformed_data,
            "metadata": {
                "total_records": len(transformed_data),
                "transformation_summary": {
                    "rules_applied": ["normalize", "categorize", "timestamp"],
                    "success_rate": 99.8,
                    "processed_at": datetime.now().isoformat()
                }
            }
        }

class EnrichProcessor(DataProcessor):
    """Data enrichment processor"""
    
    def __init__(self, process_id: str, progress_queue: Queue):
        super().__init__(process_id, progress_queue)
        self.stages = ["loading", "matching", "enriching", "validating", "completed"]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enrich process"""
        
        # Stage 1: Loading
        self.update_progress("loading", 20, "Loading enrichment sources")
        time.sleep(1.5)
        
        # Stage 2: Matching
        self.update_progress("matching", 40, "Matching records with enrichment data")
        time.sleep(2)
        
        # Stage 3: Enriching
        self.update_progress("enriching", 75, "Applying data enrichment")
        
        # Simulate enrichment
        enrichment_type = parameters.get('enrichment_type', 'demographic')
        total_records = parameters.get('total_records', 1000)
        
        enriched_data = []
        for i in range(total_records):
            if i % (total_records // 3) == 0:
                progress = 40 + (i / total_records) * 35
                self.update_progress("enriching", progress, f"Enriched {i}/{total_records} records")
            
            record = {
                "enriched_id": f"E_{i:06d}",
                "base_id": i,
                "enrichment_type": enrichment_type,
                "demographic_data": {
                    "age_group": f"group_{i % 5}",
                    "location": f"region_{i % 20}",
                    "segment": f"segment_{i % 8}"
                },
                "behavioral_data": {
                    "activity_score": round(i * 0.1 % 10, 2),
                    "engagement_level": ["low", "medium", "high"][i % 3],
                    "last_activity": datetime.now().isoformat()
                },
                "enrichment_confidence": round(0.7 + (i % 30) / 100, 2),
                "enriched_at": datetime.now().isoformat()
            }
            enriched_data.append(record)
            
            if i % 75 == 0:
                time.sleep(0.08)
        
        # Stage 4: Validating
        self.update_progress("validating", 90, "Validating enriched data quality")
        time.sleep(1)
        
        # Stage 5: Completed
        self.update_progress("completed", 100, f"Successfully enriched {len(enriched_data)} records")
        
        return {
            "operation": "enrich",
            "enrichment_type": enrichment_type,
            "records": enriched_data,
            "metadata": {
                "total_records": len(enriched_data),
                "enrichment_summary": {
                    "sources_used": ["demographic_db", "behavioral_db", "location_service"],
                    "avg_confidence": 0.85,
                    "match_rate": 95.2,
                    "processed_at": datetime.now().isoformat()
                }
            }
        }

class GenerateProcessor(DataProcessor):
    """Report/output generation processor"""
    
    def __init__(self, process_id: str, progress_queue: Queue):
        super().__init__(process_id, progress_queue)
        self.stages = ["planning", "aggregating", "formatting", "generating", "completed"]
    
    def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generate process"""
        
        # Stage 1: Planning
        self.update_progress("planning", 18, "Planning report structure")
        time.sleep(1)
        
        # Stage 2: Aggregating
        self.update_progress("aggregating", 40, "Aggregating source data")
        time.sleep(2)
        
        # Stage 3: Formatting
        self.update_progress("formatting", 65, "Formatting output structure")
        time.sleep(1.5)
        
        # Stage 4: Generating
        self.update_progress("generating", 85, "Generating final output")
        
        # Simulate generation
        output_type = parameters.get('output_type', 'summary_report')
        total_records = parameters.get('total_records', 1000)
        
        generated_data = []
        for i in range(total_records):
            if i % (total_records // 2) == 0:
                progress = 65 + (i / total_records) * 20
                self.update_progress("generating", progress, f"Generated {i}/{total_records} output records")
            
            record = {
                "report_id": f"R_{i:06d}",
                "generated_at": datetime.now().isoformat(),
                "output_type": output_type,
                "summary_metrics": {
                    "total_processed": i + 1,
                    "success_rate": round(95 + (i % 5), 2),
                    "avg_processing_time": round(2.5 + (i % 10) * 0.1, 2)
                },
                "detailed_results": {
                    "category_breakdown": {f"cat_{j}": i % (j + 1) for j in range(5)},
                    "quality_scores": [round(0.8 + (i + j) * 0.01 % 0.2, 3) for j in range(3)],
                    "trend_analysis": f"trend_{i % 4}"
                },
                "output_files": [f"{output_type}_{i}.json", f"{output_type}_{i}.csv"],
                "export_ready": True
            }
            generated_data.append(record)
            
            if i % 100 == 0:
                time.sleep(0.05)
        
        # Stage 5: Completed
        self.update_progress("completed", 100, f"Successfully generated {len(generated_data)} output records")
        
        return {
            "operation": "generate",
            "output_type": output_type,
            "records": generated_data,
            "metadata": {
                "total_records": len(generated_data),
                "generation_summary": {
                    "output_formats": ["json", "csv"],
                    "file_size_mb": round(len(generated_data) * 0.001, 2),
                    "generation_time": "real-time",
                    "export_ready": True,
                    "generated_at": datetime.now().isoformat()
                }
            }
        }

# ============================================================================
# Process Registry
# ============================================================================

class ProcessRegistry:
    """Registry for all available processes"""
    
    def __init__(self):
        self.processes = {
            ProcessType.READ: {
                "class": ReadProcessor,
                "schema": ProcessSchema(
                    name="Data Read",
                    description="Read data from various sources (database, files, APIs)",
                    parameters={
                        "source_type": "database",
                        "batch_size": 100,
                        "total_records": 1000
                    },
                    estimated_duration=30,
                    output_format="json",
                    stages=["initializing", "connecting", "reading", "validating", "completed"],
                    required_params=["source_type"]
                )
            },
            ProcessType.TRANSFORM: {
                "class": TransformProcessor,
                "schema": ProcessSchema(
                    name="Data Transform",
                    description="Transform and normalize data according to business rules",
                    parameters={
                        "transform_type": "normalize",
                        "total_records": 1000
                    },
                    estimated_duration=25,
                    output_format="json",
                    stages=["preparing", "analyzing", "transforming", "optimizing", "completed"],
                    required_params=["transform_type"]
                )
            },
            ProcessType.ENRICH: {
                "class": EnrichProcessor,
                "schema": ProcessSchema(
                    name="Data Enrich",
                    description="Enrich data with additional information from external sources",
                    parameters={
                        "enrichment_type": "demographic",
                        "total_records": 1000
                    },
                    estimated_duration=35,
                    output_format="json",
                    stages=["loading", "matching", "enriching", "validating", "completed"],
                    required_params=["enrichment_type"]
                )
            },
            ProcessType.GENERATE: {
                "class": GenerateProcessor,
                "schema": ProcessSchema(
                    name="Generate Report",
                    description="Generate reports and final outputs from processed data",
                    parameters={
                        "output_type": "summary_report",
                        "total_records": 1000
                    },
                    estimated_duration=20,
                    output_format="json",
                    stages=["planning", "aggregating", "formatting", "generating", "completed"],
                    required_params=["output_type"]
                )
            }
        }
    
    def get_process_class(self, process_type: ProcessType):
        return self.processes.get(process_type, {}).get("class")
    
    def get_process_schema(self, process_type: ProcessType):
        return self.processes.get(process_type, {}).get("schema")
    
    def get_all_schemas(self):
        return {k.value: v["schema"] for k, v in self.processes.items()}

# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, process_id: str):
        await websocket.accept()
        if process_id not in self.active_connections:
            self.active_connections[process_id] = []
        self.active_connections[process_id].append(websocket)
        logger.info(f"WebSocket connected for process {process_id}")
    
    def disconnect(self, websocket: WebSocket, process_id: str):
        if process_id in self.active_connections:
            self.active_connections[process_id].remove(websocket)
            if not self.active_connections[process_id]:
                del self.active_connections[process_id]
        logger.info(f"WebSocket disconnected for process {process_id}")
    
    async def send_personal_message(self, message: dict, process_id: str):
        if process_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[process_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[process_id].remove(conn)

# ============================================================================
# Process Manager
# ============================================================================

class ProcessManager:
    def __init__(self):
        self.manager = Manager()
        self.process_registry = self.manager.dict()
        self.progress_queues = {}
        self.active_processes = {}
        self.max_concurrent_processes = mp.cpu_count()
        self.cleanup_interval = 3600
        self.registry = ProcessRegistry()
        
    def generate_process_id(self) -> str:
        return str(uuid.uuid4())
    
    def get_active_process_count(self) -> int:
        return len([p for p in self.active_processes.values() if p.is_alive()])
    
    def start_process(self, process_name: str, parameters: Dict[str, Any]) -> str:
        """Start a new process"""
        try:
            # Validate process type
            try:
                process_type = ProcessType(process_name)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid process type: {process_name}. Available types: {[t.value for t in ProcessType]}"
                )
            
            # Check capacity
            if self.get_active_process_count() >= self.max_concurrent_processes:
                raise HTTPException(
                    status_code=429,
                    detail="Maximum concurrent processes reached"
                )
            
            process_id = self.generate_process_id()
            
            # Create progress queue
            progress_queue = Queue()
            self.progress_queues[process_id] = progress_queue
            
            # Initialize process info
            process_info = {
                'process_id': process_id,
                'name': process_name,
                'status': ProcessStatus.PENDING.value,
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
                'result': None,
                'error': None,
                'data_count': None,
                'parameters': parameters,
                'progress': None,
                'duration_seconds': None
            }
            
            self.process_registry[process_id] = process_info
            
            # Start process
            process = Process(
                target=self._execute_process,
                args=(process_id, process_type, parameters, progress_queue)
            )
            process.start()
            self.active_processes[process_id] = process
            
            logger.info(f"Started process {process_id} for {process_name}")
            return process_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to start process {process_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to start process: {str(e)}")
    
    def _execute_process(self, process_id: str, process_type: ProcessType, 
                        parameters: Dict[str, Any], progress_queue: Queue):
        """Execute the actual process"""
        start_time = time.time()
        
        try:
            # Update status to running
            process_info = dict(self.process_registry[process_id])
            process_info['status'] = ProcessStatus.RUNNING.value
            process_info['started_at'] = datetime.now().isoformat()
            self.process_registry[process_id] = process_info
            
            logger.info(f"Process {process_id} ({process_type.value}) started execution")
            
            # Get processor class and execute
            processor_class = self.registry.get_process_class(process_type)
            if not processor_class:
                raise Exception(f"No processor found for {process_type.value}")
            
            processor = processor_class(process_id, progress_queue)
            result = processor.execute(parameters)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Update with successful result
            process_info = dict(self.process_registry[process_id])
            process_info['status'] = ProcessStatus.COMPLETED.value
            process_info['completed_at'] = datetime.now().isoformat()
            process_info['result'] = result
            process_info['data_count'] = len(result.get('records', []))
            process_info['duration_seconds'] = round(duration, 2)
            self.process_registry[process_id] = process_info
            
            logger.info(f"Process {process_id} completed successfully")
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Process failed: {str(e)}"
            logger.error(f"Process {process_id} failed: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            process_info = dict(self.process_registry[process_id])
            process_info['status'] = ProcessStatus.FAILED.value
            process_info['completed_at'] = datetime.now().isoformat()
            process_info['error'] = error_msg
            process_info['duration_seconds'] = round(duration, 2)
            self.process_registry[process_id] = process_info
        
        finally:
            # Clean up progress queue
            if process_id in self.progress_queues:
                del self.progress_queues[process_id]
    
    def get_process_status(self, process_id: str) -> ProcessInfo:
        """Get process status"""
        if process_id not in self.process_registry:
            raise HTTPException(status_code=404, detail="Process not found")
        
        process_info = dict(self.process_registry[process_id])
        
        # Get latest progress if available
        if process_id in self.progress_queues:
            try:
                while not self.progress_queues[process_id].empty():
                    progress_data = self.progress_queues[process_id].get_nowait()
                    process_info['progress'] = progress_data
            except:
                pass
        
        # Convert dates
        process_info['created_at'] = datetime.fromisoformat(process_info['created_at'])
        if process_info['started_at']:
            process_info['started_at'] = datetime.fromisoformat(process_info['started_at'])
        if process_info['completed_at']:
            process_info['completed_at'] = datetime.fromisoformat(process_info['completed_at'])
        
        return ProcessInfo(**process_info)
    
    def get_process_result(self, process_id: str) -> ProcessResult:
        """Get process result"""
        process_info = self.get_process_status(process_id)
        
        if process_info.status == ProcessStatus.RUNNING:
            raise HTTPException(status_code=202, detail="Process still running")
        elif process_info.status == ProcessStatus.FAILED:
            raise HTTPException(status_code=500, detail=f"Process failed: {process_info.error}")
        elif process_info.status == ProcessStatus.PENDING:
            raise HTTPException(status_code=202, detail="Process not started yet")
        
        return ProcessResult(
            process_id=process_id,
            process_name=process_info.name,
            status=process_info.status,
            result=process_info.result,
            data_count=process_info.data_count,
            completed_at=process_info.completed_at,
            duration_seconds=process_info.duration_seconds,
            metadata={
                "created_at": process_info.created_at.isoformat(),
                "started_at": process_info.started_at.isoformat() if process_info.started_at else None,
                "parameters": dict(self.process_registry[process_id])['parameters']
            }
        )
    
    def cancel_process(self, process_id: str) -> bool:
        """Cancel a running process"""
        if process_id not in self.process_registry:
            raise HTTPException(status_code=404, detail="Process not found")
        
        if process_id in self.active_processes:
            process = self.active_processes[process_id]
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                
                process_info = dict(self.process_registry[process_id])
                process_info['status'] = ProcessStatus.CANCELLED.value
                process_info['completed_at'] = datetime.now().isoformat()
                self.process_registry[process_id] = process_info
                
                return True
        
        return False
    
    def list_processes(self, status_filter: Optional[ProcessStatus] = None, 
                      limit: int = 100, offset: int = 0) -> List[ProcessInfo]:
        """List processes with pagination"""
        processes = []
        for process_id, info in self.process_registry.items():
            process_info = dict(info)
            
            # Apply status filter
            if status_filter and process_info['status'] != status_filter.value:
                continue
            
            # Convert dates
            process_info['created_at'] = datetime.fromisoformat(process_info['created_at'])
            if process_info['started_at']:
                process_info['started_at'] = datetime.fromisoformat(process_info['started_at'])
            if process_info['completed_at']:
                process_info['completed_at'] = datetime.fromisoformat(process_info['completed_at'])
            
            processes.append(ProcessInfo(**process_info))
        
        # Sort by creation date (newest first)
        processes.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return processes[offset:offset + limit]
    
    def cleanup_completed_processes(self):
        """Clean up old processes"""
        current_time = datetime.now()
        cleanup_threshold = current_time - timedelta(seconds=self.cleanup_interval)
        
        # Clean up process objects
        to_remove = []
        for process_id, process in self.active_processes.items():
            if not process.is_alive():
                process.join(timeout=1)
                to_remove.append(process_id)
        
        for process_id in to_remove:
            del self.active_processes[process_id]
        
        # Clean up old registry entries (keep for longer for history)
        to_remove_registry = []
        for process_id, info in list(self.process_registry.items()):
            if (info.get('completed_at') and 
                datetime.fromisoformat(info['completed_at']) < cleanup_threshold):
                to_remove_registry.append(process_id)
        
        for process_id in to_remove_registry:
            del self.process_registry[process_id]

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up FastAPI application")
    
    # Start cleanup task
    async def cleanup_task():
        while True:
            try:
                process_manager.cleanup_completed_processes()
                await asyncio
