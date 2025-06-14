from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, Text, Numeric, JSON, Date, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255), nullable=False)
    logo_url = Column(Text)
    website_url = Column(Text, nullable=False)
    description = Column(Text)
    headquarters = Column(String(255))
    founded_year = Column(Integer)
    employee_count_range = Column(String(50))
    industry_category = Column(String(100), nullable=False)
    stock_symbol = Column(String(10))
    is_public = Column(Boolean, default=False)
    parent_company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'))
    status = Column(String(50), default='active')
    scraping_priority = Column(Integer, default=5)
    scraping_frequency = Column(String(20), default='weekly')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    products = relationship("Product", back_populates="company")
    documents = relationship("Document", back_populates="company")

class Product(Base):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text)
    product_url = Column(Text)
    category = Column(String(100))
    pricing_model = Column(String(50))
    target_audience = Column(String(100))
    launch_date = Column(Date)
    status = Column(String(50), default='active')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    company = relationship("Company", back_populates="products")
    documents = relationship("Document", back_populates="product")

class Document(Base):
    __tablename__ = 'documents'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'))
    document_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    source_url = Column(Text, nullable=False)
    language = Column(String(10), default='en')
    jurisdiction = Column(String(100))
    effective_date = Column(Date)
    last_modified = Column(Date)
    version_identifier = Column(String(100))
    status = Column(String(50), default='active')
    file_path = Column(Text)
    file_size = Column(BigInteger)
    file_hash = Column(String(64))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime)

    company = relationship("Company", back_populates="documents")
    product = relationship("Product", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = 'document_versions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    raw_content = Column(Text)
    content_hash = Column(String(64), nullable=False)
    word_count = Column(Integer)
    character_count = Column(Integer)
    file_path = Column(Text)
    extracted_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="versions")
    analysis = relationship("DocumentAnalysis", back_populates="version")

class DocumentAnalysis(Base):
    __tablename__ = 'document_analysis'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_version_id = Column(UUID(as_uuid=True), ForeignKey('document_versions.id'), nullable=False)
    overall_score = Column(Numeric(4,2), nullable=False)
    complexity_score = Column(Numeric(4,2))
    readability_score = Column(Numeric(4,2))
    sentiment_score = Column(Numeric(4,2))
    confidence_level = Column(Numeric(3,2))
    analysis_version = Column(String(20), nullable=False)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    version = relationship("DocumentVersion", back_populates="analysis")

# ... Add other models as needed (Clause, ClauseType, User, etc.) ...