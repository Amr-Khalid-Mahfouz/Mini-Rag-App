from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATE_SUCCEEDED = "file_validate_succeeded"
    FILE_TYPE_NOT_SUPPORT = "file_type_not_supported"
    FILE_SIZE_EXCEEDED = "file_size_exceeded"

    FILE_UPLOAD_SUCCEEDED = "file_upload_succeeded"
    FILE_UPLOAD_FAILED = "file_upload_fail"
    
    FILE_PROCESSING_FAILED = "file_processing_failed"
    FILE_PROCESSING_SUCCEEDED = "file_processing_succeeded"
    
    NO_FILES_ERROR = 'no_files_were_found'
    FILE_ID_ERROR = "no_file_found_with_this_id"

    PORJECT_NOT_FOUND = "porject_is_not_found"
    INSERTION_INTO_VECTORDB_ERROR = "insertion_into_vectordb_failed"
    INSERTION_INTO_VECTORDB_SUCCEEDED = "insertion_into_vectordb_succeeded"
    
    COLLECTION_SEARCH_FAILED = "collection_was_not_found"
    COLLECTION_SEARCH_SUCCEEDED = "collection_was_found"

    ANSWER_RAG_FAILED = "rag_answer_generation_failed"
    ANSWER_RAG_SUCCEEDED = "rag_answer_generation_succeeded"
