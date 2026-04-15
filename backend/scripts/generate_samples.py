import os
import sys

# Try to import reportlab, if not found, provide instructions
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
except ImportError:
    print("Error: 'reportlab' library is required to generate sample PDFs.")
    print("Please install it using: pip install reportlab")
    sys.exit(1)

def create_pdf(output_dir, filename, title, content):
    path = os.path.join(output_dir, filename)
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))
    
    # Content
    for line in content.split('\n'):
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 6))
    
    doc.build(story)
    print(f"Created {path}")

# Data for English PDFs
documents = {
    "rodo.pdf": {
        "title": "Data Protection Policy (GDPR)",
        "content": """This document outlines the company's commitment to data protection and privacy in accordance with GDPR regulations.
        All employees are responsible for ensuring that personal data is processed lawfully, fairly, and transparently.
        Personal data must be collected for specified, explicit, and legitimate purposes and not further processed in a manner that is incompatible with those purposes.
        The company implements appropriate technical and organizational measures to ensure a level of security appropriate to the risk."""
    },
    "Devops.pdf": {
        "title": "DevOps Practices and Standards",
        "content": """Our DevOps culture focuses on automation, monitoring, and continuous integration/continuous deployment (CI/CD).
        Developers are responsible for their code from development to production.
        Standard tools include Docker for containerization, Kubernetes for orchestration, and GitHub Actions for CI/CD pipelines.
        Infrastructure as Code (IaC) is mandatory for all new infrastructure components, using Terraform or CloudFormation."""
    },
    "podrecznik_kultury.pdf": {
        "title": "Company Culture Handbook",
        "content": """Our values: Innovation, Transparency, and Customer Success.
        We believe in a flat organizational structure where every voice matters.
        Feedback is a gift - we encourage regular 1-on-1 meetings and open communication.
        Work-life balance is essential for long-term productivity and employee well-being."""
    },
    "hr_policy.pdf": {
        "title": "Human Resources Policy",
        "content": """General guidelines for employment, benefits, and workplace conduct.
        The company is an equal opportunity employer and does not tolerate discrimination or harassment.
        Paid Time Off (PTO): Employees are entitled to 25 days of vacation per year.
        Sick leave: Please inform your manager before 9:00 AM if you are unable to work due to illness."""
    },
    "standardy.pdf": {
        "title": "Coding Standards and Best Practices",
        "content": """All code must be reviewed by at least one other developer before merging.
        Write clean, maintainable code following SOLID principles.
        Documentation is required for all public APIs and complex business logic.
        Unit tests are mandatory for all new features, aiming for at least 80% code coverage."""
    }
}

if __name__ == "__main__":
    # Determine the project root (assumed to be two levels up from this script)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    output_dir = os.path.join(project_root, "test_sources")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    for filename, data in documents.items():
        create_pdf(output_dir, filename, data["title"], data["content"])

    print("\nSample PDFs generated successfully in 'test_sources/' directory.")
