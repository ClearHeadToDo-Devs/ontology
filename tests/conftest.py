"""
Pytest configuration and fixtures for Actions Vocabulary testing.
"""

import pytest
import rdflib
from pyshacl import validate
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import tempfile
import os

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "data"
ROOT_DIR = Path(__file__).parent.parent
RESULTS_DIR = Path(__file__).parent / "results"

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def ontology_graph():
    """Load the actions vocabulary ontology graph."""
    g = rdflib.Graph()
    ontology_path = ROOT_DIR / "actions-vocabulary.ttl"
    if not ontology_path.exists():
        pytest.fail(f"Ontology file not found: {ontology_path}")
    g.parse(ontology_path, format="turtle")
    return g


@pytest.fixture(scope="session")
def shapes_graph():
    """Load the SHACL shapes graph."""
    g = rdflib.Graph()
    shapes_path = ROOT_DIR / "actions-shapes.ttl"
    if not shapes_path.exists():
        pytest.fail(f"SHACL shapes file not found: {shapes_path}")
    g.parse(shapes_path, format="turtle")
    return g


@pytest.fixture
def shacl_validator(ontology_graph, shapes_graph):
    """Create a SHACL validator function using pyshacl library."""
    
    def validate_data(
        data_graph: rdflib.Graph,
        save_report: bool = True,
        test_name: str = "test",
        use_ontology: bool = True
    ) -> Tuple[bool, rdflib.Graph, str]:
        """
        Validate data graph against shapes using pyshacl library.
        
        Args:
            data_graph: The RDF data to validate
            save_report: Whether to save validation report to file
            test_name: Name for the validation report file
            use_ontology: Whether to include ontology for validation
        
        Returns:
            Tuple of (conforms, report_graph, report_text)
        """
        conforms, report_graph, report_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            ont_graph=ontology_graph if use_ontology else None,
            inference='rdfs' if use_ontology else None,
            abort_on_first=False,
            debug=False
        )
        
        # Save validation report if requested
        if save_report:
            report_file = RESULTS_DIR / f"{test_name}-result.ttl"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return conforms, report_graph, report_text
    
    return validate_data


@pytest.fixture
def data_loader():
    """Utility to load test data from files."""
    
    def load_data(file_path: Path, format="turtle") -> rdflib.Graph:
        """Load RDF data from file."""
        g = rdflib.Graph()
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        g.parse(file_path, format=format)
        return g
    
    return load_data


@pytest.fixture
def test_data_files():
    """Get dictionaries of valid and invalid test data files."""
    valid_files = {}
    invalid_files = {}
    
    # Collect valid test files
    valid_dir = TEST_DATA_DIR / "valid"
    if valid_dir.exists():
        for file_path in valid_dir.glob("*.ttl"):
            valid_files[file_path.stem] = file_path
    
    # Also include top-level valid files
    for file_path in TEST_DATA_DIR.glob("valid-*.ttl"):
        valid_files[file_path.stem] = file_path
    
    # Collect invalid test files  
    invalid_dir = TEST_DATA_DIR / "invalid"
    if invalid_dir.exists():
        for file_path in invalid_dir.glob("*.ttl"):
            invalid_files[file_path.stem] = file_path
    
    # Also include top-level invalid files
    for file_path in TEST_DATA_DIR.glob("invalid-*.ttl"):
        invalid_files[file_path.stem] = file_path
    
    return {"valid": valid_files, "invalid": invalid_files}


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--verbose-validation", 
        action="store_true", 
        default=False,
        help="Show detailed SHACL validation output"
    )
    parser.addoption(
        "--quick", 
        action="store_true", 
        default=False,
        help="Run only basic tests (skip complex/slow cases)"
    )
    parser.addoption(
        "--save-reports",
        action="store_true",
        default=True,
        help="Save validation reports to results directory"
    )


@pytest.fixture
def verbose_validation(request):
    """Get verbose validation setting."""
    return request.config.getoption("--verbose-validation")


@pytest.fixture
def quick_mode(request):
    """Get quick mode setting."""
    return request.config.getoption("--quick")


@pytest.fixture  
def save_reports(request):
    """Get save reports setting."""
    return request.config.getoption("--save-reports")


def pytest_collection_modifyitems(config, items):
    """Mark tests based on naming conventions."""
    for item in items:
        # Mark slow tests
        if "complex" in item.name or "hierarchy" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark validation tests
        if "shacl" in str(item.fspath) or "validation" in item.name:
            item.add_marker(pytest.mark.validation)


def pytest_configure(config):
    """Configure test session."""
    # Ensure results directory exists
    RESULTS_DIR.mkdir(exist_ok=True)
    
    # Add custom markers
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "validation: marks tests as SHACL validation")


def pytest_report_header(config):
    """Add custom header to test report."""
    return [
        f"Actions Vocabulary Test Suite",
        f"Test data directory: {TEST_DATA_DIR}",
        f"Results directory: {RESULTS_DIR}",
        f"Quick mode: {config.getoption('--quick')}",
        f"Verbose validation: {config.getoption('--verbose-validation')}"
    ]