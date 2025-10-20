"""
SHACL validation tests using pyshacl library.

Tests validation against the Actions Vocabulary using dedicated test data files.
"""

import pytest
from pathlib import Path
from .utils import (
    assert_validation_passes,
    assert_validation_fails,
    get_violation_details,
    print_validation_summary,
    count_validation_violations
)


class TestValidDataFiles:
    """Test that valid test data files pass SHACL validation."""
    
    def test_all_valid_files_pass(
        self, 
        shacl_validator, 
        data_loader, 
        test_data_files, 
        verbose_validation,
        quick_mode
    ):
        """Test that all valid data files pass validation."""
        valid_files = test_data_files["valid"]
        
        if not valid_files:
            pytest.skip("No valid test data files found")
        
        failed_files = []
        
        for file_name, file_path in valid_files.items():
            # Skip complex tests in quick mode
            if quick_mode and ("complex" in file_name or "hierarchy" in file_name):
                continue
                
            try:
                data_graph = data_loader(file_path)
                conforms, report_graph, report_text = shacl_validator(
                    data_graph, 
                    test_name=f"valid-{file_name}"
                )
                
                if verbose_validation:
                    print_validation_summary(conforms, report_graph, file_name, verbose=True)
                
                if not conforms:
                    failed_files.append((file_name, report_text))
                    
            except Exception as e:
                failed_files.append((file_name, f"Exception: {e}"))
        
        if failed_files:
            error_msg = "The following valid files failed validation:\n"
            for file_name, error in failed_files:
                error_msg += f"  - {file_name}: {error[:200]}...\n"
            pytest.fail(error_msg)
    
    @pytest.mark.parametrize("file_name", [
        "minimal-root-action",
        "root-with-project", 
        "valid-simple",
    ])
    def test_specific_valid_file(
        self, 
        shacl_validator,
        data_loader, 
        test_data_files,
        verbose_validation,
        file_name
    ):
        """Test specific valid files individually."""
        valid_files = test_data_files["valid"]
        
        if file_name not in valid_files:
            pytest.skip(f"Valid test file {file_name} not found")
        
        file_path = valid_files[file_name]
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name=f"specific-valid-{file_name}"
        )
        
        if verbose_validation and not conforms:
            print(f"\nValidation report for {file_name}:\n{report_text}")
        
        assert_validation_passes(
            conforms, 
            report_text, 
            f"Valid file {file_name} should pass validation"
        )


class TestInvalidDataFiles:
    """Test that invalid test data files fail SHACL validation."""
    
    def test_all_invalid_files_fail(
        self,
        shacl_validator,
        data_loader,
        test_data_files, 
        verbose_validation,
        quick_mode
    ):
        """Test that all invalid data files fail validation."""
        invalid_files = test_data_files["invalid"] 
        
        if not invalid_files:
            pytest.skip("No invalid test data files found")
        
        unexpected_passes = []
        
        for file_name, file_path in invalid_files.items():
            # Skip complex tests in quick mode
            if quick_mode and ("examples" in file_name or "complex" in file_name):
                continue
                
            try:
                data_graph = data_loader(file_path)
                conforms, report_graph, report_text = shacl_validator(
                    data_graph,
                    test_name=f"invalid-{file_name}"
                )
                
                if verbose_validation:
                    print_validation_summary(conforms, report_graph, file_name, verbose=True)
                
                if conforms:
                    unexpected_passes.append(file_name)
                else:
                    # Count violations for reporting
                    violation_count = count_validation_violations(report_graph)
                    if verbose_validation:
                        print(f"  Expected violations found: {violation_count}")
                        
            except Exception as e:
                # File loading/parsing errors are also test failures
                unexpected_passes.append(f"{file_name} (Exception: {e})")
        
        if unexpected_passes:
            error_msg = "The following invalid files unexpectedly passed validation:\n"
            for file_name in unexpected_passes:
                error_msg += f"  - {file_name}\n"
            pytest.fail(error_msg)
    
    @pytest.mark.parametrize("file_name", [
        "root-with-parent",
        "wrong-depth-sequence",
        "leaf-with-children", 
        "invalid-priority",
        "invalid-context-format",
        "missing-required-properties"
    ])
    def test_specific_invalid_file(
        self,
        shacl_validator,
        data_loader,
        test_data_files,
        verbose_validation,
        file_name
    ):
        """Test specific invalid files individually."""
        invalid_files = test_data_files["invalid"]
        
        if file_name not in invalid_files:
            pytest.skip(f"Invalid test file {file_name} not found")
        
        file_path = invalid_files[file_name]
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name=f"specific-invalid-{file_name}"
        )
        
        if verbose_validation:
            print(f"\nValidation report for {file_name}:\n{report_text}")
        
        assert_validation_fails(
            conforms,
            report_text, 
            f"Invalid file {file_name} should fail validation"
        )
        
        # Verify we get meaningful violations
        violations = get_violation_details(report_graph)
        assert len(violations) > 0, f"Expected violations for {file_name}"


class TestRecurrenceValidation:
    """Test recurrence-specific validation scenarios."""
    
    def test_valid_recurrence_file(
        self,
        shacl_validator,
        data_loader, 
        test_data_files,
        verbose_validation
    ):
        """Test valid recurrence pattern."""
        valid_files = test_data_files["valid"]
        
        if "recurrence-action" not in valid_files:
            pytest.skip("recurrence-action test file not found")
        
        file_path = valid_files["recurrence-action"]
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name="recurrence-valid"
        )
        
        if verbose_validation and not conforms:
            print(f"\nRecurrence validation report:\n{report_text}")
        
        assert_validation_passes(
            conforms,
            report_text,
            "Valid recurrence action should pass"
        )
    
    def test_invalid_recurrence_both_termination(
        self,
        shacl_validator,
        data_loader,
        test_data_files,
        verbose_validation
    ):
        """Test invalid recurrence with both until and count."""
        invalid_files = test_data_files["invalid"]
        
        if "recurrence-both-termination" not in invalid_files:
            pytest.skip("recurrence-both-termination test file not found")
        
        file_path = invalid_files["recurrence-both-termination"]
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name="recurrence-both-termination"
        )
        
        if verbose_validation:
            print(f"\nRecurrence validation report:\n{report_text}")
        
        assert_validation_fails(
            conforms,
            report_text,
            "Recurrence with both until and count should fail"
        )


class TestTemporalValidation:
    """Test temporal constraint validation scenarios."""
    
    def test_temporal_inconsistency(
        self,
        shacl_validator,
        data_loader,
        test_data_files,
        verbose_validation
    ):
        """Test temporal inconsistency (completion before schedule)."""
        invalid_files = test_data_files["invalid"]
        
        if "temporal-inconsistency" not in invalid_files:
            pytest.skip("temporal-inconsistency test file not found")
        
        file_path = invalid_files["temporal-inconsistency"] 
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name="temporal-inconsistency"
        )
        
        if verbose_validation:
            print(f"\nTemporal validation report:\n{report_text}")
        
        assert_validation_fails(
            conforms,
            report_text,
            "Completion before schedule should fail validation"
        )


@pytest.mark.slow
class TestComplexHierarchy:
    """Test complex hierarchical validation scenarios."""
    
    def test_complete_hierarchy(
        self,
        shacl_validator,
        data_loader,
        test_data_files,
        verbose_validation,
        quick_mode
    ):
        """Test complete 5-level hierarchy."""
        if quick_mode:
            pytest.skip("Skipping complex hierarchy test in quick mode")
        
        valid_files = test_data_files["valid"]
        
        if "hierarchy-complete" not in valid_files:
            pytest.skip("hierarchy-complete test file not found")
        
        file_path = valid_files["hierarchy-complete"]
        data_graph = data_loader(file_path)
        conforms, report_graph, report_text = shacl_validator(
            data_graph,
            test_name="hierarchy-complete"
        )
        
        if verbose_validation and not conforms:
            print(f"\nHierarchy validation report:\n{report_text}")
        
        assert_validation_passes(
            conforms,
            report_text,
            "Complete hierarchy should pass validation"
        )