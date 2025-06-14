class EventBus:
    """Event bus for inter-component communication"""
    
    async def publish(self, event: BaseEvent):
        """Publish event to all subscribers"""
        pass
    
    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to specific event type"""
        pass

@dataclass
class DocumentScrapedEvent(BaseEvent):
    """Published when document is successfully scraped"""
    company_id: UUID
    document_id: UUID
    document_type: str
    has_changes: bool

@dataclass
class AnalysisCompletedEvent(BaseEvent):
    """Published when document analysis is completed"""
    document_id: UUID
    analysis_id: UUID
    overall_score: float
    flagged_issues: List[str]