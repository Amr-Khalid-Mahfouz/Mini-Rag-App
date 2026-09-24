from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATE_SCUCCEDED = "file_validate_success"
    FILE_TYPE_NOT_SUPPORT = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_UPLOAD_SUCCEDED = "file_upload_succes"
    FILE_UPLOAD_FAILED = "file_upload_fail"
    FILE_PROCESSING_FAILED = "file_processing_failed"
    FILE_PROCESSING_SUCCEDED = "file_processing_succeded"