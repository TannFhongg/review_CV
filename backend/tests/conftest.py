"""Shared test fixtures and configuration."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def sample_jd_text() -> str:
    """Sample Job Description text for testing."""
    return """
    Senior C++ Software Engineer — Automotive

    Company: TechAuto GmbH
    Location: Ho Chi Minh City, Vietnam
    Employment Type: Full-time

    Requirements:
    - 3+ years of experience in C++ development
    - Strong knowledge of Qt framework (Qt Widgets, QML)
    - Experience with Linux development and embedded systems
    - Familiarity with automotive protocols (CAN, LIN, UDS)
    - Version control with Git
    - Good communication skills in English

    Preferred:
    - Experience with Docker and CI/CD
    - Knowledge of AUTOSAR
    - Experience with Agile/Scrum methodology

    Responsibilities:
    - Develop and maintain C++ applications for automotive ECU testing
    - Design and implement Qt-based GUI applications
    - Collaborate with cross-functional teams
    - Write unit tests and perform code reviews
    - Document software architecture and design decisions
    """


@pytest.fixture
def sample_cv_text() -> str:
    """Sample CV text for testing."""
    return """
    VO VAN TUAN
    Fresher C++ Software Engineer

    Email: tuanvo@example.com
    Phone: +84 123 456 789
    GitHub: github.com/tuanvo
    Location: Ho Chi Minh City, Vietnam

    EDUCATION
    Ho Chi Minh City University of Technology (HCMUT)
    Bachelor of Engineering — Computer Engineering
    2020 - 2024
    GPA: 3.2/4.0

    PROJECTS

    VTuber Avatar Control Panel
    - Developed a Qt Widgets application for controlling VTuber avatar states
    - Implemented interactive UI controls using signal/slot communication
    - Technologies: C++, Qt Widgets, Qt Creator

    Embedded Weather Station
    - Built a weather monitoring system on Raspberry Pi with Embedded Linux
    - Sensor data acquisition via I2C/SPI protocols
    - Technologies: C, Embedded Linux, Raspberry Pi, Python

    Smart Home Controller
    - Designed a home automation system using ESP32
    - Implemented CAN bus communication between modules
    - Technologies: C++, FreeRTOS, CAN protocol

    TECHNICAL SKILLS
    - Languages: C++, C, Python
    - Frameworks: Qt, FreeRTOS
    - Tools: Git, VS Code, Qt Creator
    - Platforms: Linux, Raspberry Pi, ESP32

    LANGUAGES
    - Vietnamese: Native
    - English: Intermediate (IELTS 6.0)
    """


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async HTTP client for API testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
