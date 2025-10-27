#!/usr/bin/env python3
"""
Build script for Actions Vocabulary v3 Extensions

This script prepares the modular ontology extensions for deployment by:
1. Creating the directory structure
2. Copying OWL files to deployment locations
3. Converting to multiple RDF formats (TTL, RDF/XML, JSON-LD)
4. Generating basic HTML documentation

Usage:
    python build_extensions.py
    python build_extensions.py --output-dir ./site
"""

import argparse
import shutil
from pathlib import Path
import sys

try:
    import rdflib
    from rdflib import Graph
except ImportError:
    print("⚠️  rdflib not installed. Install with: uv pip install rdflib")
    print("   Continuing with basic file copying only...")
    rdflib = None


def create_directory_structure(output_dir: Path):
    """Create the deployment directory structure"""
    print("📁 Creating directory structure...")

    dirs = [
        output_dir / "actions" / "v3" / "core",
        output_dir / "actions" / "v3" / "context",
        output_dir / "actions" / "v3" / "workflow",
        output_dir / "actions" / "v3" / "roles",
        output_dir / "actions" / "v3" / "agile",
        output_dir / ".well-known",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {d}")

    return dirs


def copy_owl_files(output_dir: Path):
    """Copy OWL files to deployment locations"""
    print("\n📄 Copying OWL files...")

    files = {
        "actions-vocabulary.owl": output_dir / "actions" / "v3" / "core" / "vocabulary.owl",
        "actions-context.owl": output_dir / "actions" / "v3" / "context" / "extension.owl",
        "actions-workflow.owl": output_dir / "actions" / "v3" / "workflow" / "extension.owl",
        "actions-roles.owl": output_dir / "actions" / "v3" / "roles" / "extension.owl",
    }

    for src, dest in files.items():
        src_path = Path(src)
        if src_path.exists():
            shutil.copy2(src_path, dest)
            print(f"  ✓ {src} → {dest.relative_to(output_dir)}")
        else:
            print(f"  ⚠️  {src} not found, skipping")


def convert_to_formats(output_dir: Path):
    """Convert OWL files to multiple RDF formats"""
    if not rdflib:
        print("\n⚠️  Skipping format conversion (rdflib not available)")
        return

    print("\n🔄 Converting to multiple formats...")

    modules = {
        "core": output_dir / "actions" / "v3" / "core",
        "context": output_dir / "actions" / "v3" / "context",
        "workflow": output_dir / "actions" / "v3" / "workflow",
        "roles": output_dir / "actions" / "v3" / "roles",
    }

    for module, module_dir in modules.items():
        owl_file = module_dir / ("vocabulary.owl" if module == "core" else "extension.owl")

        if not owl_file.exists():
            continue

        print(f"\n  {module}:")

        try:
            g = Graph()
            g.parse(str(owl_file), format="xml")

            # Turtle
            ttl_file = module_dir / ("vocabulary.ttl" if module == "core" else "extension.ttl")
            g.serialize(str(ttl_file), format="turtle")
            print(f"    ✓ {ttl_file.name}")

            # RDF/XML
            rdf_file = module_dir / ("vocabulary.rdf" if module == "core" else "extension.rdf")
            g.serialize(str(rdf_file), format="pretty-xml")
            print(f"    ✓ {rdf_file.name}")

            # JSON-LD
            jsonld_file = module_dir / ("vocabulary.jsonld" if module == "core" else "extension.jsonld")
            g.serialize(str(jsonld_file), format="json-ld")
            print(f"    ✓ {jsonld_file.name}")

        except Exception as e:
            print(f"    ❌ Error converting {module}: {e}")


def generate_html_docs(output_dir: Path):
    """Generate basic HTML documentation for each module"""
    print("\n📝 Generating HTML documentation...")

    modules = {
        "core": {
            "title": "Actions Vocabulary Core",
            "description": "Core vocabulary for action planning and execution with BFO/CCO alignment.",
        },
        "context": {
            "title": "Context Extension",
            "description": "Formalizes GTD-style contexts as first-class BFO entities linked to CCO infrastructure.",
        },
        "workflow": {
            "title": "Workflow Extension",
            "description": "Adds dependency modeling and workflow patterns for sequential and parallel action execution.",
        },
        "roles": {
            "title": "Roles Extension",
            "description": "Integrates CCO Agent and Role infrastructure for assignment, delegation, and Areas of Focus.",
        },
    }

    for module, info in modules.items():
        module_dir = output_dir / "actions" / "v3" / module
        index_file = module_dir / "index.html"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{info['title']} - Actions Vocabulary</title>
    <style>
        body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
        .formats {{ background: #f8f9fa; padding: 1rem; border-radius: 4px; margin: 2rem 0; }}
        .formats h2 {{ margin-top: 0; font-size: 1.2rem; }}
        .formats ul {{ list-style: none; padding: 0; }}
        .formats li {{ margin: 0.5rem 0; }}
        code {{ background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>{info['title']}</h1>
    <p>{info['description']}</p>

    <div class="formats">
        <h2>Available Formats</h2>
        <ul>
            <li>📄 <a href="{"vocabulary" if module == "core" else "extension"}.owl">OWL/XML</a> - OWL ontology in XML syntax</li>
            <li>📄 <a href="{"vocabulary" if module == "core" else "extension"}.ttl">Turtle</a> - RDF in Turtle syntax</li>
            <li>📄 <a href="{"vocabulary" if module == "core" else "extension"}.rdf">RDF/XML</a> - RDF in XML syntax</li>
            <li>📄 <a href="{"vocabulary" if module == "core" else "extension"}.jsonld">JSON-LD</a> - RDF in JSON-LD syntax</li>
        </ul>
    </div>

    <h2>Usage</h2>
    <p>Import this ontology in your OWL files:</p>
    <pre><code>&lt;owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/{module}"/&gt;</code></pre>

    <h2>Documentation</h2>
    <ul>
        <li><a href="https://github.com/yourusername/ontology/blob/main/PHASE2_DESIGN.md">Design Documentation</a></li>
        <li><a href="https://github.com/yourusername/ontology/blob/main/BFO_CCO_ALIGNMENT.md">BFO/CCO Alignment</a></li>
    </ul>

    <hr style="margin: 3rem 0;">
    <p style="color: #6c757d; font-size: 0.9rem;">
        Part of the <a href="../../..">Actions Vocabulary</a> |
        <a href="https://vocab.clearhead.io">vocab.clearhead.io</a>
    </p>
</body>
</html>
"""

        with open(index_file, "w") as f:
            f.write(html)

        print(f"  ✓ {module}/index.html")


def create_root_index(output_dir: Path):
    """Create root index.html for the vocabulary"""
    print("\n🏠 Creating root index...")

    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actions Vocabulary - Modular Productivity Ontology</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }
        .module { background: #f8f9fa; padding: 1.5rem; margin: 1rem 0; border-radius: 4px; border-left: 4px solid #3498db; }
        .module h3 { margin-top: 0; }
        code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Actions Vocabulary v3</h1>
    <p>A modular, BFO/CCO-aligned ontology for personal and organizational productivity.</p>

    <h2>Modules</h2>

    <div class="module">
        <h3>Core Vocabulary</h3>
        <p>Foundation classes: ActionPlan, ActionProcess, hierarchical structure, and states.</p>
        <p><a href="actions/v3/core/">📄 Browse</a> | <code>https://vocab.clearhead.io/actions/v3/core</code></p>
    </div>

    <div class="module">
        <h3>Context Extension</h3>
        <p>GTD-style contexts as typed entities (Location, Tool, Energy, Social).</p>
        <p><a href="actions/v3/context/">📄 Browse</a> | <code>https://vocab.clearhead.io/actions/v3/context</code></p>
    </div>

    <div class="module">
        <h3>Workflow Extension</h3>
        <p>Dependencies, blocking relationships, and workflow patterns.</p>
        <p><a href="actions/v3/workflow/">📄 Browse</a> | <code>https://vocab.clearhead.io/actions/v3/workflow</code></p>
    </div>

    <div class="module">
        <h3>Roles Extension</h3>
        <p>Agent assignment, delegation, and GTD Areas of Focus using CCO infrastructure.</p>
        <p><a href="actions/v3/roles/">📄 Browse</a> | <code>https://vocab.clearhead.io/actions/v3/roles</code></p>
    </div>

    <h2>Quick Start</h2>
    <pre><code># Import core + extensions in your ontology
&lt;owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/&gt;
&lt;owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/context"/&gt;
&lt;owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/workflow"/&gt;
&lt;owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/roles"/&gt;</code></pre>

    <h2>Documentation</h2>
    <ul>
        <li><a href="https://github.com/yourusername/ontology">GitHub Repository</a></li>
        <li><a href="https://github.com/yourusername/ontology/blob/main/PHASE2_DESIGN.md">Phase 2 Design Document</a></li>
        <li><a href="https://github.com/yourusername/ontology/blob/main/BFO_CCO_ALIGNMENT.md">BFO/CCO Alignment Guide</a></li>
    </ul>

    <hr style="margin: 3rem 0;">
    <p style="color: #6c757d;">Version 3.1.0 | <a href="https://vocab.clearhead.io">vocab.clearhead.io</a></p>
</body>
</html>
"""

    index_file = output_dir / "index.html"
    with open(index_file, "w") as f:
        f.write(index_html)

    print(f"  ✓ index.html")


def main():
    parser = argparse.ArgumentParser(description="Build Actions Vocabulary extensions for deployment")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("site"),
        help="Output directory for built site (default: ./site)",
    )
    parser.add_argument(
        "--skip-conversion",
        action="store_true",
        help="Skip RDF format conversion (OWL only)",
    )
    args = parser.parse_args()

    print("🚀 Building Actions Vocabulary v3 Extensions\n")
    print(f"Output directory: {args.output_dir.absolute()}\n")

    # Create structure
    create_directory_structure(args.output_dir)

    # Copy OWL files
    copy_owl_files(args.output_dir)

    # Convert to formats
    if not args.skip_conversion:
        convert_to_formats(args.output_dir)

    # Generate HTML
    generate_html_docs(args.output_dir)
    create_root_index(args.output_dir)

    print("\n✅ Build complete!")
    print(f"\nNext steps:")
    print(f"  1. Test locally: cd {args.output_dir} && python -m http.server 8000")
    print(f"  2. View at: http://localhost:8000")
    print(f"  3. Deploy to GitHub Pages or Netlify")


if __name__ == "__main__":
    main()
