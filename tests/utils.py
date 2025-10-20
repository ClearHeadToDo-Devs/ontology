"""
Utility functions for SHACL validation testing.
"""

import rdflib
from typing import List, Dict, Any
from rdflib import Namespace

# SHACL namespace
SHACL = Namespace("http://www.w3.org/ns/shacl#")


def count_validation_violations(validation_graph: rdflib.Graph) -> int:
    """
    Count SHACL validation violations in report graph.
    
    Args:
        validation_graph: The SHACL validation report graph
        
    Returns:
        Number of violations found
    """
    violations = list(validation_graph.subjects(
        SHACL.conforms, 
        rdflib.Literal(False)
    ))
    return len(violations)


def get_violation_messages(validation_graph: rdflib.Graph) -> List[str]:
    """
    Extract violation messages from validation report.
    
    Args:
        validation_graph: The SHACL validation report graph
        
    Returns:
        List of violation messages
    """
    messages = []
    for violation in validation_graph.subjects(rdflib.RDF.type, SHACL.ValidationResult):
        for message in validation_graph.objects(violation, SHACL.resultMessage):
            messages.append(str(message))
    return messages


def get_violation_details(validation_graph: rdflib.Graph) -> List[Dict[str, Any]]:
    """
    Get detailed violation information from validation report.
    
    Args:
        validation_graph: The SHACL validation report graph
        
    Returns:
        List of dictionaries containing violation details
    """
    violations = []
    for violation in validation_graph.subjects(rdflib.RDF.type, SHACL.ValidationResult):
        violation_info = {}
        
        # Get message
        for message in validation_graph.objects(violation, SHACL.resultMessage):
            violation_info['message'] = str(message)
        
        # Get focus node  
        for focus in validation_graph.objects(violation, SHACL.focusNode):
            violation_info['focus_node'] = str(focus)
        
        # Get result path
        for path in validation_graph.objects(violation, SHACL.resultPath):
            violation_info['path'] = str(path)
        
        # Get severity
        for severity in validation_graph.objects(violation, SHACL.resultSeverity):
            violation_info['severity'] = str(severity)
        
        # Get constraint component
        for component in validation_graph.objects(violation, SHACL.sourceConstraintComponent):
            violation_info['constraint'] = str(component)
            
        violations.append(violation_info)
    
    return violations


def assert_validation_passes(conforms: bool, report_text: str, message: str = ""):
    """
    Assert that validation passes with detailed error reporting.
    
    Args:
        conforms: Whether validation conformed
        report_text: The validation report text
        message: Custom error message
        
    Raises:
        AssertionError: If validation failed
    """
    if not conforms:
        error_msg = f"{message}\nValidation failed with report:\n{report_text}"
        raise AssertionError(error_msg)


def assert_validation_fails(conforms: bool, report_text: str, message: str = ""):
    """
    Assert that validation fails as expected.
    
    Args:
        conforms: Whether validation conformed
        report_text: The validation report text  
        message: Custom error message
        
    Raises:
        AssertionError: If validation unexpectedly passed
    """
    if conforms:
        error_msg = f"{message}\nValidation unexpectedly passed"
        raise AssertionError(error_msg)
    
    # Ensure we have some violation messages
    if not report_text or ("ValidationResult" not in report_text and "Constraint Violation" not in report_text):
        error_msg = f"{message}\nValidation failed but no detailed violations found"
        raise AssertionError(error_msg)


def print_validation_summary(
    conforms: bool, 
    validation_graph: rdflib.Graph, 
    test_name: str,
    verbose: bool = False
):
    """
    Print formatted validation summary.
    
    Args:
        conforms: Whether validation conformed
        validation_graph: The validation report graph
        test_name: Name of the test
        verbose: Whether to show detailed violation info
    """
    if conforms:
        print(f"✅ {test_name}: PASSED")
    else:
        violations = get_violation_details(validation_graph)
        print(f"❌ {test_name}: FAILED ({len(violations)} violations)")
        
        if verbose:
            for i, violation in enumerate(violations, 1):
                print(f"  {i}. {violation.get('message', 'Unknown violation')}")
                if 'focus_node' in violation:
                    print(f"     Focus: {violation['focus_node']}")
                if 'path' in violation:
                    print(f"     Path: {violation['path']}")


def create_test_graph_from_string(turtle_data: str) -> rdflib.Graph:
    """
    Create test graph from turtle string data.
    
    Args:
        turtle_data: RDF data in Turtle format
        
    Returns:
        Parsed RDF graph
    """
    g = rdflib.Graph()
    g.parse(data=turtle_data, format="turtle")
    return g


def get_all_test_files(test_data_dir, pattern="*.ttl"):
    """
    Get all test files matching pattern.
    
    Args:
        test_data_dir: Directory containing test files
        pattern: Glob pattern to match files
        
    Returns:
        Dictionary mapping file stems to file paths
    """
    files = {}
    test_path = test_data_dir
    if test_path.exists():
        for file_path in test_path.glob(pattern):
            files[file_path.stem] = file_path
    return files