"""
Test fixtures for the python-zeep-codegen test suite.

This module provides pytest fixtures that are shared across multiple test files,
including sample XSD/WSDL files, temporary directories, and mock objects.
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from typing import Generator


@pytest.fixture
def temp_test_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test outputs.
    
    Yields:
        Path to temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="zeep_test_"))
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_xsd_file() -> Path:
    """
    Path to the sample-complex.xsd test file.
    
    Returns:
        Path to the sample XSD file
    """
    return Path(__file__).parent.parent / "sample-complex.xsd"


@pytest.fixture
def sample_wsdl_file() -> Path:
    """
    Path to the sample.wsdl test file.
    
    Returns:
        Path to the sample WSDL file
    """
    return Path(__file__).parent.parent / "sample.wsdl"


@pytest.fixture
def simple_xsd_content() -> str:
    """
    Simple XSD content for basic testing.
    
    Returns:
        String containing minimal valid XSD
    """
    return '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/test"
           xmlns:tns="http://example.com/test"
           elementFormDefault="qualified">
    
    <xs:complexType name="PersonType">
        <xs:sequence>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="age" type="xs:int"/>
            <xs:element name="email" type="xs:string" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:element name="Person" type="tns:PersonType"/>
</xs:schema>
'''


@pytest.fixture
def simple_xsd_file(temp_test_dir: Path) -> Path:
    """
    Create a simple XSD file for testing.
    
    Args:
        temp_test_dir: Temporary directory fixture
    
    Returns:
        Path to created XSD file
    """
    xsd_file = temp_test_dir / "simple.xsd"
    xsd_file.write_text('''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/test"
           xmlns:tns="http://example.com/test"
           elementFormDefault="qualified">
    
    <xs:complexType name="PersonType">
        <xs:sequence>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="age" type="xs:int"/>
            <xs:element name="email" type="xs:string" minOccurs="0"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:element name="Person" type="tns:PersonType"/>
</xs:schema>
''')
    return xsd_file
